# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 19:34:52 2019

@author: kbhandari
"""

def prepare_data(input_file):
    
    import pandas as pd
    import numpy as np
    import os
    
    path = r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks"
    os.chdir(path)
    df = pd.read_csv(input_file + ".csv")
    df=df.sort_index(ascending=0)
    
    cols = [col for col in df.columns if col not in ('Date', 'Close Price')]
    
    df[cols] = df[cols].shift(1)
    
    #Feature Engineering
    # Closing Price Difference
    df['Difference_2'] = df['Close Price'].shift(1) - df['Close Price'].shift(2)
    # Moving Average
    df['MA_2'] = df['Close Price'].shift(1).rolling(window=2).mean()
    df['MA_7'] = df['Close Price'].shift(1).rolling(window=7).mean()
    # Compute Volatility using the pandas rolling standard deviation function
    df['Log_Ret'] = np.log(df['Close Price'].shift(1)/ df['Close Price'].shift(2))
    df['Volatility_7'] = df['Log_Ret'].rolling(window=7).std() * np.sqrt(7)
    
    df.columns = [str(col) + '_' + input_file if col != 'Date' else str(col) for col in df.columns]
    
    return df

import pandas as pd
import numpy as np
yes_bank = prepare_data("YESBANK")
kotak_bank = prepare_data("KOTAK")
hdfc_bank = prepare_data("HDFC_BANK")
sbi = prepare_data("SBI")
list_of_datasets = [kotak_bank,hdfc_bank,sbi]

for dataset in list_of_datasets:
    yes_bank = pd.merge(yes_bank,right=dataset, how='left', on ='Date')
#yes_bank['Date'] = yes_bank['Date'].astype('datetime64')

sentiments = pd.read_csv(r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks\MoneyControl_Comments.csv")
from datetime import time, timedelta
sentiments.Creation_Date = sentiments.Creation_Date.astype('datetime64')

start = time(0, 0, 0).strftime('%H:%M')
end = time(9, 0, 0).strftime('%H:%M')
sentiments['Creation_Date'] = np.where(sentiments.Creation_Date.dt.strftime('%H:%M').between(start,end),sentiments['Creation_Date'] - timedelta(days=1), sentiments['Creation_Date'])
sentiments['Creation_Date'] = np.where(sentiments.Creation_Date.dt.dayofweek == 5,sentiments['Creation_Date'] - timedelta(days=1),
                              np.where(sentiments.Creation_Date.dt.dayofweek == 6,sentiments['Creation_Date'] - timedelta(days=2), sentiments['Creation_Date']))

daily_sentiments = sentiments.groupby([sentiments.Creation_Date.astype('datetime64').dt.strftime('%d-%B-%Y')])['SCNLP_MC_Very_Negative','SCNLP_MC_Negative','SCNLP_MC_Neutral','SCNLP_MC_Positive','SCNLP_MC_Very_Positive'].mean().reset_index()    
yes_bank = pd.merge(yes_bank,right=daily_sentiments, how='left', left_on =['Date'], right_on = ['Creation_Date']).drop(['Creation_Date'],axis=1)
yes_bank.to_csv('data.csv', index = False)
