import pandas as pd
import numpy as np
import dask.dataframe as dd

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_trans_count.parquet'
result = dd.read_parquet(path).set_index('trans_id').persist()


##############

result['trans_bins_id'] = result['trans_id'] + '_' + result['bins']
bad_filt = result['time']==99
bad_trans_bins = result[bad_filt]['trans_bins_id'].unique()
result = result[~bad_filt].persist()

result[['meter_id','day']] = result['trans_id'].str.split('_', expand=True)
result['day'] = result['day'].astype(int)
result = result.sort_values(['meter_id','day']).reset_index(drop=True)
result = result.persist()
# got counts
print('got observed')
print(len(bad_trans_bins))

##############

bins = [0, 9, 12, 15, 18.00001, 24]
labels = [
    '12a to {}a'.format(bins[1]),    # 12 - 9?
    '{}a to {}p'.format(bins[1], round(bins[2])), # 9 - 12
    '{}p to {}p'.format(round(bins[2]), bins[3]-12), # 12 - 3
    '{}p to {}p'.format(bins[3]-12, round(bins[4])-12), # 3 - 6
    '{}p to 12a'.format(round(bins[4])-12)
    ]
good_bins = labels[1:-1]

##############

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\Meter_Regular_Operating_Good.csv'
regs = pd.read_csv(path)[['block_id','meter_id']]

regs['meter_id'] = regs['meter_id'].astype(str)
result['meter_id'] = result['meter_id'].astype(str)

regs = result[['meter_id','trans_id']].drop_duplicates().set_index('meter_id').join(
    regs.set_index('meter_id'), how='inner'
    ).reset_index()
new_regs = []
[
    new_regs.extend([
        row + [binny] for binny in good_bins
    ])
    for row in regs.values.tolist()
]
regs = pd.DataFrame(new_regs, columns = list(regs)+['bins'])
make_cols = ['meter_id','day']
regs[make_cols] = regs['trans_id'].str.split('_', expand=True)

regs['trans_bins_id'] = regs['trans_id'] + '_' + regs['bins']

join_col = 'trans_bins_id'
joining_cols = [col for col in list(result) if col not in make_cols+['trans_id','bins']]
regs = regs.set_index(join_col).join(result[joining_cols].set_index(join_col), how='left').fillna(value=0).reset_index()
regs = regs[~regs[join_col].isin(bad_trans_bins)]


path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_join_reqs.parquet'
result.to_parquet(path, engine='pyarrow')