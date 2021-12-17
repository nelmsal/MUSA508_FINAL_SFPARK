import pandas as pd
import datetime as dt

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\SFMTA_Parking_Meter_Detailed_Revenue_Transactions.csv'
park19 = pd.read_csv(
    path,
    usecols=['TRANSMISSION_DATETIME', 'POST_ID', 'STREET_BLOCK', 'SESSION_START_DT', 'SESSION_END_DT', 'GROSS_PAID_AMT']
    )
print('Import Done')

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\Meter_Regular_Operating.csv'
regs = pd.read_csv(path)
reg_ids = set(regs['meter_id'].unique())
reg_filt = park19['POST_ID'].isin(reg_ids)
park19 = park19[reg_filt]
print('only regular meters')
print(len(park19[~reg_filt]))

date_string_format = '%Y/%m/%d %I:%M:%S %p'
for mark in ['START', 'END']:
    park19['SESSION_{}_STR'.format(mark)] = park19['SESSION_{}_DT'.format(mark)]
    park19['SESSION_{}_DT'.format(mark)] = pd.to_datetime(
        park19['SESSION_{}_DT'.format(mark)],
        format = date_string_format,
        errors = 'coerce',
        cache = True
        )
    print('{} Done'.format(mark))

park19['SESSION_HR_DIFF'] = (park19['SESSION_END_DT'] - park19['SESSION_START_DT']) / pd.Timedelta('1 hour')
#park19 = park19[park19['SESSION_HR_DIFF']>=0]
low_time_cutoff = .016666
# ONE MINUTE
high_time_cutoff = 9
# NINE HOURS
park19 = park19[(park19['SESSION_HR_DIFF']>low_time_cutoff)&(park19['SESSION_HR_DIFF']<=high_time_cutoff)]
print('Diff')
park19['SESSION_DATE'] = park19['SESSION_START_DT'].dt.date
park19['SESSION_DAY_OF_WEEK'] = park19['SESSION_START_DT'].dt.day_name()
park19 = park19[park19['SESSION_DAY_OF_WEEK']!='Sunday']
print('date')

holidays = ['2019-01-21','2019-02-18', '2019-05-27', '2019-07-04', '2019-09-02', '2019-10-14', '2019-11-11', '2019-11-28', '2019-11-29','2019-12-25']
holidays = [dt.datetime.strptime(day, '%Y-%m-%d').date() for day in holidays]
park19 = park19[(~park19['SESSION_DATE'].isin(holidays))]
print('holidays')

# time bins
bins = [0, 7, 9, 12, 15, 18, 21, 24]
labels = [
    '12a to {}a'.format(bins[1]),    # 12 - 7?
    '{}a to {}a'.format(bins[1], bins[2]), # 7 - 9
    '{}a to {}p'.format(bins[2], bins[3]), # 9 - 12
    '{}p to {}p'.format(bins[3], bins[4]-12), # 12 - 3
    '{}p to {}p'.format(bins[4]-12, bins[5]-12), # 3 - 6
    '{}p to {}p'.format(bins[5]-12, bins[6]-12), # 6 - 9
    '{}p to 12a'.format(bins[6]-12)  # 9 - midnight
    ]

for mark in ['START', 'END']:
    park19['SESSION_{}_DAY'.format(mark)] = park19['SESSION_{}_DT'.format(mark)].dt.dayofyear
    park19['SESSION_{}_HOUR'.format(mark)] = park19['SESSION_{}_DT'.format(mark)].dt.hour
    park19['SESSION_{}_TIME'.format(mark)] = park19['SESSION_{}_HOUR'.format(mark)] + (park19['SESSION_{}_DT'.format(mark)].dt.minute/60)
park19 = park19.loc[park19['SESSION_START_DAY']==park19['SESSION_END_DAY']]
park19 = park19[park19['SESSION_END_TIME']>9]
print('dates')

# diff 
for mark in ['START', 'END']:
    park19['SESSION_{}_BIN'.format(mark)] = pd.cut(
        park19['SESSION_{}_HOUR'.format(mark)], 
        bins, 
        labels=labels, 
        right=False, include_lowest=True
        )
park19['diff_bin'] = True
park19.loc[park19['SESSION_START_BIN']==park19['SESSION_END_BIN'], 'diff_bin'] = False
print('time bins')

start_bins = ['12a to 7a','7a to 9a']
end_bins = ['6p to 9p','9p to 12a']
bad_bins = list(start_bins + end_bins)

park19['diff_bin'] = True
park19.loc[park19['SESSION_START_BIN']==park19['SESSION_END_BIN'], 'diff_bin'] = False

dif_filt = (park19['diff_bin']==False)
bad_bins_filt = (park19['SESSION_START_BIN'].isin(bad_bins))
park19 = park19[~(dif_filt&bad_bins_filt)]

start_filt = (park19['SESSION_START_BIN'].isin(start_bins) & park19['SESSION_END_BIN'].isin(start_bins))
end_filt = (park19['SESSION_START_BIN'].isin(end_bins) & park19['SESSION_END_BIN'].isin(end_bins))
too_far_filt = (park19['SESSION_START_BIN'].isin(['12a to 7a']) | park19['SESSION_END_BIN'].isin(['9p to 12a']))
park19 = park19[~(too_far_filt|start_filt|end_filt)]
print('pure time bins filter')

park19['trans_id'] = park19['POST_ID'].astype(str) + '_' + park19['SESSION_START_DAY'].astype(str)
print('transaction id')
# start_group = park19.groupby('trans_id')['SESSION_START_STR'].count().reset_index()
# group_remove = set(start_group[start_group['SESSION_START_STR']==1]['trans_id'].unique())
# park19 = park19[~park19['trans_id'].isin(group_remove)]
# print('remove single transaction rows')
# print(len(group_remove))

col_rename = {
    'TRANSMISSION_DATETIME': 'trans_use_id',
    'POST_ID': 'meter_id',
    'trans_id':'trans_id',
    'STREET_BLOCK':'block_id',
    'GROSS_PAID_AMT': 'payment',

    'SESSION_DATE': 'date',
    'SESSION_DAY_OF_WEEK': 'day_of_week',
    'SESSION_START_DAY': 'day',

    'SESSION_START_DT': 'start_datetime',
    'SESSION_START_STR': 'start_datetime_str',
    'SESSION_START_TIME': 'start_time',
    'SESSION_START_HOUR': 'start_hour',
    'SESSION_START_BIN': 'start_bin',

    'SESSION_END_DT': 'end_datetime',
    'SESSION_END_STR': 'end_datetime_str',
    #'SESSION_END_DAY': 'end_date',
    'SESSION_END_TIME': 'end_time',
    'SESSION_END_HOUR': 'end_hour',
    'SESSION_END_BIN': 'end_bin',

    'SESSION_HR_DIFF': 'diff_hour',
    'diff_bin': 'diff_bin'
}
col_rename = {old:new for old,new in col_rename.items() if old in list(park19)}
park19 = park19.rename(columns=col_rename)[col_rename.values()]
print('renames')

good_ids = set(park19['meter_id'].unique())
good_ids = {r for r in reg_ids if r in good_ids}
path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\Meter_Regular_Operating_Good.csv'
regs = regs[regs['meter_id'].isin(good_ids)]
regs.to_csv(path)
print('get regular ids')
print(len(regs))

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_transactions.parquet'
park19.to_parquet(path, engine='pyarrow')
print('exported')