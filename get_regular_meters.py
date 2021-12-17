import pandas as pd 

path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\Meter_Operating_Schedules.csv'
regs = pd.read_csv(path)
sch_filt = regs['Schedule Type']=='Operating Schedule'
no_sun = regs['Days Applied']!='Su'

bad_uses = ['Yellow - Commercial loading zone', 'Black - Motorcycle parking',
       'Red - Six wheeled truck loading zone', 'Brown -', 'Purple -']

regs = regs[sch_filt&no_sun].sort_values('Post ID')
regs_y = regs.loc[regs['Applied Color Rule'].isin(bad_uses), 'Post ID'].unique() 
regs = regs[~regs['Post ID'].isin(regs_y)]
regs[['Street and Block','Post ID']].rename(columns={
    'Street and Block':'block_id','Post ID':'meter_id'
}).drop_duplicates().reset_index(drop=True).to_csv(r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\Meter_Regular_Operating.csv')