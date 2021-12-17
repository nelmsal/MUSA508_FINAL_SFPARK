import pandas as pd
import numpy as np
import dask.dataframe as dd

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_trans_day_clean.parquet'
trans_day_actions = dd.read_parquet(path).set_index('trans_id').persist()

#############

def round_down(value, decimals):
    factor = 1 / (10 ** decimals)
    return (value // factor) * factor

bins = [0, 9, 12, 15, 18.00001, 24]
labels = [
    '12a to {}a'.format(bins[1]),    # 12 - 9?
    '{}a to {}p'.format(bins[1], round(bins[2])), # 9 - 12
    '{}p to {}p'.format(round(bins[2]), bins[3]-12), # 12 - 3
    '{}p to {}p'.format(bins[3]-12, round(bins[4])-12), # 3 - 6
    '{}p to 12a'.format(round(bins[4])-12)
    ]
good_bins = labels[1:-1]

#############

cut_off_time = 9
trans_day_actions = trans_day_actions[trans_day_actions['time']>=cut_off_time].drop_duplicates()
trans_day_actions = trans_day_actions.persist()

trans_day_actions['bins'] = pd.cut(
            trans_day_actions['time'], 
            bins, 
            labels=labels, 
            right=False, include_lowest=True
            ).astype(str)
trans_day_actions = trans_day_actions[trans_day_actions['bins'].isin(good_bins)]
trans_day_actions['block_day_bins'] = trans_day_actions['trans_id'] + '_' + trans_day_actions['bins']
trans_day_actions = trans_day_actions[['block_day_bins', 'time']].set_index('block_day_bins')
trans_day_actions = trans_day_actions.persist()

#####

unique_list = list(trans_day_actions.index.unique().compute())
trans_day_actions = trans_day_actions.repartition(divisions=sorted(unique_list + [unique_list[-1]]))
print(trans_day_actions.npartitions)

#############

counter = 0
cols = ['time'] #,'count']
def get_times(row):
    #start_ends = row[['time', 'action']].values.tolist()

    global counter
    counter = counter + 1
    if float(counter/100000).is_integer():
        print(counter)

    try:
        start_ends = row[['time']].values.tolist()
        start_ends = np.reshape(start_ends, (round(len(start_ends)/2), 2))

        start_ends = [round_down(end-start,3) for start,end in start_ends]
        return pd.Series((sum(start_ends), len(start_ends)), index=cols)

    except:
        #print(row[['time', 'action']].values.tolist())
        return pd.Series((99, 99), index=cols)
    #group_hours_actions_df = hours_actions_df.groupby(['bins', 'action'])['time'].apply(list) #.count()

trans_day_actions = trans_day_actions.map_partitions(get_times, meta={'time': 'int64', 'action': 'str'})
#trans_day_actions = trans_day_actions.groupby('bins').apply(get_times)

#####

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_trans_count.parquet'
trans_day_actions.to_parquet(path, engine='pyarrow')
print('exported')
