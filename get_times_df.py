import pandas as pd
import datetime as dt

def get_times_df(path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\SFMTA_Parking_Meter_Detailed_Revenue_Transactions.csv'):
    park19 = pd.read_csv(
        path,
        usecols=['TRANSMISSION_DATETIME', 'POST_ID', 'STREET_BLOCK', 'SESSION_START_DT', 'SESSION_END_DT', 'GROSS_PAID_AMT']
        )
    print('Import Done')
    date_string_format = '%Y/%m/%d %I:%M:%S %p'
    park19['SESSION_START_DT'] = pd.to_datetime(
        park19['SESSION_START_DT'],
        format = date_string_format,
        errors = 'coerce',
        cache = True
        )
    print('Start Done')
    park19['SESSION_END_DT'] = pd.to_datetime(
        park19['SESSION_END_DT'],
        format = date_string_format,
        errors = 'coerce',
        cache = True
        )
    print('End Done')
    
    # path = r'C:\Users\nelms\Documents\Penn\MUSA-508\MUSA508_FINAL_SFPARK\meter_transactions.parquet'
    # park19.to_parquet(path, engine='pyarrow')
    return(park19)
