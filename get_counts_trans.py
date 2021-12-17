import pandas as pd
import numpy as np
import dask.dataframe as dd

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_starts_ends.parquet'
trans_day_actions = dd.read_parquet(path).set_index('trans_id') #.persist()

# #############

# unique_list = list(hours_actions_df.index.unique().compute())
# hours_actions_df = hours_actions_df.repartition(divisions=sorted(unique_list + [unique_list[-1]]))
# print(trans_day_actions.npartitions)

#################

counter = 0

def grouper(row, cut_off_time=9):
    hours_actions = row[['time','action']].values.tolist()

    global counter
    counter = counter + 1
    if float(counter/10000).is_integer():
        print(counter)

    while hours_actions[0][1] == 'interval':
        hours_actions.pop(0)

    while hours_actions[-1][1] == 'interval':
        hours_actions.pop(-1)

    past_action = ''
    keep = []
    for hour, action in hours_actions:
        if (action != 'interval')and(action==past_action):
            if action == 'start':
                pass
            elif action == 'end':
                keep.pop()
                past_hour = hour
                past_action = action
                keep.append([hour, action])
        elif action!=past_action:
            # if action == 'end':
            #     if (hour == 18)or(hour == 18.0):
            #         hour = 17.99999
            #     elif (hour == 12)or(hour == 12.0):
            #         hour = 11.99999
            #     elif (hour == 15)or(hour == 15.0):
            #         hour = 14.99999
            past_action = action
            keep.append([hour, action])
    hours_actions = keep
    #start_count = len([act for hr,act in keep if act=='start'])

    past_action = ''
    keep = []
    for hour, action in hours_actions:
        if (action == 'interval'):
            if(past_action == 'start'):
                correct_end = hour-.00001
                # if (hour == 18)or(hour == 18.0):
                #     correct_end = 17.99999
                # if (hour == 12)or(hour == 12.0):
                #     correct_end = 11.99999
                keep.append([correct_end,'end'])
                keep.append([hour,'start'])
                past_action = 'start'
            else:
                pass
        else:
            past_action = action
            keep.append([hour, action])
            
    hours_actions = keep
    past_action = ''
    keep = []
    for hour, action in hours_actions:
        if action==past_action:
            pass
        elif action!=past_action:
            past_hour = hour
            past_action = action
            keep.append([hour, action])
    #start_count = len([act for hr,act in keep if act=='start'])

    # hours_actions_df = pd.DataFrame(keep, columns=['time','action'])
    return pd.DataFrame(keep, columns=['time','action'])

#trans_day_actions = hours_actions_df.map_partitions(grouper, meta={'time': 'int64', 'action': 'str'})
trans_day_actions = trans_day_actions.groupby('trans_id')[['time','action']].apply(grouper, meta={'time': 'int64', 'action': 'str'})
trans_day_actions = trans_day_actions #.persist()

print('after function')

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_trans_day_clean.parquet'
trans_day_actions.to_parquet(path, engine='pyarrow')
print('exported')