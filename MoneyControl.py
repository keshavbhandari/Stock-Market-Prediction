# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 18:27:05 2019

@author: kbhandari
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
import re
from datetime import datetime, timedelta
from pycorenlp import StanfordCoreNLP
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#Run this in Anaconda CMD:
#cd C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks\stanford-corenlp-full-2018-10-05\stanford-corenlp-full-2018-10-05
#java -mx6g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 5000

#import stanfordnlp
#stanfordnlp.download('en')
nlp = StanfordCoreNLP('http://localhost:9000')

def get_sentiments(url, filepath, first_time=False):
    def time_formatter(Date, Date_Formatted):
        time_format = '%H.%M %p %b %d %Y'
        if 'hr' in Date:
            hr = re.findall(r"(\d+) hr", Date)[0]
        else: hr = 0
        if 'min' in Date:
            mins = re.findall(r"(\d+) min", Date)[0]
        else: mins = 0
        t = datetime.strptime(Date_Formatted.lstrip(' ').replace('th',' 2019').replace('rd',' 2019').replace('st',' 2019').replace('nd',' 2019'), time_format)-timedelta(hours=int(hr), minutes=int(mins))
        return t.strftime("%d-%b-%Y %H:%M")
    
    chrome_driver = r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks\chromedriver.exe"
    driver = webdriver.Chrome(chrome_driver)
    driver.set_page_load_timeout(45)
    driver.get(url)
    time.sleep(2)
    driver.refresh()
    time.sleep(2)
    delay = 3 # seconds
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, 'Support')))
        print ("Page is ready!")
    except TimeoutException:
        print ("Loading took too much time!")
    nav_btn = driver.find_element_by_link_text("Support")
    time.sleep(2)
    driver.execute_script("arguments[0].scrollIntoView();", nav_btn)
    time.sleep(300)
    
    html = driver.page_source
    driver.quit()
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class':'clearfix'})
    table = soup.findAll('li',attrs={'class':'pstdl'})
    user, text, date = [],[],[]
    for x in table:    
        try:
            user.append(x.find('img').get('alt'))
            text.append(x.find('p',{"class":"txt14gry MT5 lnht20"}).text)
            date.append(x.find('div',{"class":"link13gry"}).text)
        except:
            pass
    
    rows = list(zip(user,text,date))
    df = pd.DataFrame(rows, columns=['User','Text','Date'])
    df['Date_Formatted'] = df['Date']
    
    df.Date_Formatted = df.Date_Formatted.apply(lambda x: datetime.now().strftime(" %H.%M %p %b %d %Y") if 'about' in x else x)
    df['Creation_Date'] = df.apply(lambda x: time_formatter(x['Date'],x['Date_Formatted']), axis=1)
    df.drop(['Date', 'Date_Formatted'], axis=1, inplace=True)
    
    #Sentiment Analysis
    df_text = df.Text.tolist()
    
    def batch_wise_caller(df_text):
        SCORES= []
        analyzer = SentimentIntensityAnalyzer()
        
        for text in df_text:
        
            stnfrd_scores= sentiment_score(text) 
            blob = TextBlob(text)
            blob_scores = list(blob.sentiment)
            vs = analyzer.polarity_scores(text)
            scores = stnfrd_scores + blob_scores + [vs['pos']] + [vs['compound']] + [vs['neu']] + [vs['neg']]
    
            SCORES.append(scores)
    
        return SCORES


    
    def sentiment_score(data):
        result = nlp.annotate(data,
                       properties={
                           'annotators': 'sentiment, pos',
                           'outputFormat': 'json',
                           'timeout': 100000,
                       })
        return result['sentences'][0]['sentimentDistribution']
    
    
    my_scores = batch_wise_caller(df_text)
    new_df = pd.DataFrame(my_scores,columns=['SCNLP_MC_Very_Negative','SCNLP_MC_Negative','SCNLP_MC_Neutral','SCNLP_MC_Positive','SCNLP_MC_Very_Positive','TB_MC_Polarity','TB_MC_Subjectivity','VD_MC_Positive','VD_MC_Compound','VD_MC_Neutral','VD_MC_Negative'])
    final_df = pd.concat([df,new_df], axis=1)
    
    if first_time == True:
        #Write file
        final_df.to_csv(filepath, index=False)
    else:
        #Append to database
        database = pd.read_csv(filepath)
        database_nrows = len(database.index)
        final_df = final_df.append(database, ignore_index = True)
        final_df_nrows = len(final_df.index)
        final_df['Creation_Date'] = final_df['Creation_Date'].astype('datetime64')
        final_df = final_df.drop_duplicates(subset=['User','Text'], keep='first').sort_values('Creation_Date', ascending = False).reset_index(drop=True)
        if final_df_nrows > database_nrows:
            final_df.to_csv(filepath, index=False)
        
    return True

get_sentiments(url = "https://mmb.moneycontrol.com/forum-topics/stocks/kotak-mahindra-3441.html",
               filepath = r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks\KOTAK\MoneyControl_Comments.csv",
               first_time = False)

get_sentiments(url = "https://mmb.moneycontrol.com/forum-topics/stocks/yes-bank-246084.html",
               filepath = r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks\YESBANK\MoneyControl_Comments.csv",
               first_time = False)

get_sentiments(url = "https://mmb.moneycontrol.com/forum-topics/stocks/hdfc-bank-4962.html",
               filepath = r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks\HDFC_BANK\MoneyControl_Comments.csv",
               first_time = False)

get_sentiments(url = "https://mmb.moneycontrol.com/forum-topics/stocks/sbi-406.html",
               filepath = r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks\SBI\MoneyControl_Comments.csv",
               first_time = False)

get_sentiments(url = "https://mmb.moneycontrol.com/forum-topics/stocks/axis-bank-3142.html",
               filepath = r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks\AXIS_BANK\MoneyControl_Comments.csv",
               first_time = False)