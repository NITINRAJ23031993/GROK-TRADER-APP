import os, pandas as pd
if __name__=='__main__':
    if os.path.exists('data/ticks.csv'):
        df = pd.read_csv('data/ticks.csv', parse_dates=['time']).set_index('time')
        os.makedirs('data', exist_ok=True)
        df.to_parquet('data/ticks.parquet')
        print('Converted ticks.csv -> ticks.parquet')
    else:
        print('No data/ticks.csv found. Provide tick CSV to use tick-replay.')