import pandas as pd
import numpy as np
import dask.dataframe as dd

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_starts_ends.parquet'
hours_actions_df = dd.read_parquet(path).set_index('trans_id').persist()

#############

unique_list = list(hours_actions_df.index.unique().compute())
hours_actions_df = hours_actions_df.repartition(divisions=sorted(unique_list + [unique_list[-1]]))
print(hours_actions_df.npartitions)

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

#################

counter = 0

def grouper(row, cut_off_time=9, bins=bins, labels=labels, good_bins = good_bins):
    hours_actions = row[['time','action']].values.tolist()

    global counter
    counter = counter + 1
    if float(counter/100000).is_integer():
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

trans_day_actions = hours_actions_df.map_partitions(grouper, meta={'time': 'int64', 'action': 'str'})
#trans_day_actions = hours_actions_df.groupby('trans_id')[['time','action']].apply(grouper, meta={'time': 'int64', 'action': 'str'})
trans_day_actions = trans_day_actions.persist()

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_trans_day_clean.parquet'
trans_day_actions.to_parquet(path, engine='pyarrow')
print('exported')