import pandas as pd
import datetime as dt
# import os 
# path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK'
# os.chdir(path)

final_cols = ['trans_id','time','action']
pull_cols = ['trans_id', 'day', 'start_time', 'end_time']

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_transactions.parquet'
park19 = pd.read_parquet(path, columns=pull_cols)
print(len(park19))

def get_starts_ends(park_df, final_cols = ['trans_id','time','action'], bins = [0, 7, 9, 12, 15, 18, 21, 24]):
    starts = park_df[['trans_id', 'day', 'start_time']].rename(columns={'start_time':'time'})
    starts['action'] = 'start'

    ends = park_df[['trans_id', 'day', 'end_time']].rename(columns={'end_time':'time'})
    ends['action'] = 'end'
    
    start_group = starts.groupby('trans_id')['action'].count().reset_index()
    group_remove = set(start_group[start_group['action']==1]['trans_id'].unique())
    
    starts = starts[~starts['trans_id'].isin(group_remove)][final_cols]
    ends = ends[~ends['trans_id'].isin(group_remove)][final_cols]

    trans_ids = set(starts['trans_id'].unique())
    
    bin_list = []
    [
        [
            #bin_list.extend([[tid, ttime, 'start'],[tid, ttime, 'end']])
            bin_list.append([tid, ttime, 'interval'])
            for ttime in bins
            ]
        for tid in trans_ids
    ]
    bins_df = pd.DataFrame(bin_list, columns=final_cols)
    start_ends = pd.concat([starts, ends, bins_df]).sort_values(['trans_id','time']).reset_index(drop=True)
    return start_ends
start_ends = get_starts_ends(park19, bins = [7, 9, 12, 15, 18, 21], final_cols=final_cols)

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_starts_ends.parquet'
start_ends.to_parquet(path, engine='pyarrow')
print('exported')