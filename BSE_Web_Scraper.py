# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 20:05:23 2019

@author: kbhandari
"""

from selenium import webdriver
import time
from bs4 import BeautifulSoup
import pandas as pd

chrome_driver = r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks\chromedriver.exe"
driver = webdriver.Chrome(chrome_driver)
driver.set_page_load_timeout(30)
driver.get("https://in.investing.com/equities/yes-bank-historical-data")
time.sleep(3)
driver.find_element_by_id("widgetFieldDateRange").click()
time.sleep(2)
driver.find_element_by_id("startDate").clear()
time.sleep(1)
driver.find_element_by_id("startDate").send_keys("10/06/2017")
time.sleep(1)
driver.find_element_by_id("applyBtn").click()
time.sleep(4)
html = driver.page_source
driver.close()
driver.quit()
soup = BeautifulSoup(html, 'html.parser')

table = soup.find('table', {'class': 'genTbl closedTbl historicalTbl'})

table_head = table.find('thead')
header = []    
for th in table_head.findAll('th'):
    key = th.get_text()
    if key != 'Date':
        key = 'DV' + '_' + key
        key = key.replace('%','').replace('/','_').replace('.','').replace(' ','').replace('+','')
    header.append(key)

l = []
for tr in table.findAll('tr'):
    td = tr.find_all('td')
    if len(td) > 0:
        row = [tr.text for tr in td]
        l.append(row)

dv_table = pd.DataFrame(l, columns=header)
dv_table = dv_table[[col for col in dv_table.columns if 'Date' in col or 'Price' in col or 'Vol' in col]]




###########################################################################
def scraper(url, table_class, table_id, start_date, response, table_filter = False):
    
    from selenium import webdriver
    from selenium.webdriver.support.ui import Select
    import time
    from bs4 import BeautifulSoup
    import pandas as pd
    
    chrome_driver = r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks\chromedriver.exe"
    driver = webdriver.Chrome(chrome_driver)
    driver.set_page_load_timeout(45)
    
    base_url = "https://in.investing.com"
    driver.get(url)
    time.sleep(3)
    
    #Filter
    if table_filter == False:
        pass
    else:
        mySelect = Select(driver.find_element_by_id("stocksFilter"))
        mySelect.select_by_visible_text(table_filter)
        time.sleep(3)
    
    #Getting names and URLs from table
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': table_class, 'id': table_id})
    element = list()
    for a in table.findAll('a', href=True):
        if a.get_text().upper() != response.upper():
            element.append((a.get_text(), base_url + a['href']))
    
    #Getting historic data for each element
    n = len(element)
    i = 1
    first_time = True
    for info in element:
        print(info[0], ": ", i, "out of", n)
        i += 1
        driver.get(info[1])
        time.sleep(2)
        nav_btn = driver.find_element_by_link_text("Add to Portfolio")
        time.sleep(2)
        driver.execute_script("arguments[0].scrollIntoView();", nav_btn)
        time.sleep(2)
        driver.find_element_by_link_text("Historical Data").click()
        time.sleep(2)
        driver.find_element_by_id("widgetFieldDateRange").click()
        time.sleep(2)
        driver.find_element_by_id("startDate").clear()
        time.sleep(2)
        driver.find_element_by_id("startDate").send_keys(start_date)
        time.sleep(2)
        driver.find_element_by_id("applyBtn").click()
        time.sleep(5)
        html = driver.page_source
    
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'genTbl closedTbl historicalTbl'})
        
        #Table Headers
        table_head = table.find('thead')
        header = []    
        for th in table_head.findAll('th'):
            key = th.get_text()
            if key != 'Date':
                key = info[0] + '_' + key
            key = key.replace('%','').replace('/','_').replace('.','').replace(' ','').replace('+','')
            header.append(key)
        
        #Table Rows
        l = []
        for tr in table.findAll('tr'):
            td = tr.find_all('td')
            if len(td) > 0:
                row = [tr.text for tr in td]
                l.append(row)
        
        #Check for empty table
        if l[0][0] == 'No results found':
            pass
        else:
            if first_time:
                universe = pd.DataFrame(l, columns=header)
                universe = universe[[col for col in universe.columns if 'Date' in col or 'Price' in col or 'Vol' in col]]
                first_time = False
            else:
                df = pd.DataFrame(l, columns=header)
                df = df[[col for col in df.columns if 'Date' in col or 'Price' in col or 'Vol' in col]]
                universe = pd.merge(universe,df,on='Date')
        
    driver.close()
    driver.quit()
    return universe


currency = scraper(url = "https://in.investing.com/currencies/streaming-forex-rates-majors",
                   table_class = 'genTbl closedTbl crossRatesTbl',
                   start_date = "10/06/2017")

energy = scraper(url = "https://in.investing.com/commodities/",
                   table_class = 'genTbl closedTbl crossRatesTbl',
                   table_id = 'energy',
                   start_date = "10/06/2017")

metals = scraper(url = "https://in.investing.com/commodities/",
                   table_class = 'genTbl closedTbl crossRatesTbl',
                   table_id = 'metals',
                   start_date = "10/06/2017")

agriculture = scraper(url = "https://in.investing.com/commodities/",
                   table_class = 'genTbl closedTbl crossRatesTbl',
                   table_id = 'agriculture',
                   start_date = "10/06/2017")

commodities_indices = scraper(url = "https://in.investing.com/commodities/",
                   table_class = 'genTbl closedTbl crossRatesTbl',
                   table_id = 'commodities_indices',
                   start_date = "10/06/2017")

india_indice = scraper(url = "https://in.investing.com/indices/",
                   table_class = 'genTbl openTbl',
                   table_id = 'main_page_box_id_43',
                   start_date = "10/06/2017")

eu_indice = scraper(url = "https://in.investing.com/indices/",
                   table_class = 'genTbl openTbl',
                   table_id = 'main_page_box_id_39',
                   start_date = "10/06/2017")

america_indice = scraper(url = "https://in.investing.com/indices/",
                   table_class = 'genTbl openTbl',
                   table_id = 'main_page_box_id_1',
                   start_date = "10/06/2017")

asia_pacific_indice = scraper(url = "https://in.investing.com/indices/",
                   table_class = 'genTbl openTbl',
                   table_id = 'main_page_box_id_3',
                   start_date = "10/06/2017")

niftybank = scraper(url = "https://in.investing.com/equities/india",
                   table_class = 'genTbl closedTbl crossRatesTbl elpTbl elp25',
                   table_id = 'cross_rate_markets_stocks_1',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = "Nifty Bank")

etf_equity = scraper(url = "https://in.investing.com/etfs/",
                   table_class = 'genTbl closedTbl crossRatesTbl elpTbl elp40',
                   table_id = 'etf_eq',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

etf_comm = scraper(url = "https://in.investing.com/etfs/",
                   table_class = 'genTbl closedTbl crossRatesTbl elpTbl elp40',
                   table_id = 'etf_comm',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

etf_curr = scraper(url = "https://in.investing.com/etfs/",
                   table_class = 'genTbl closedTbl crossRatesTbl elpTbl elp40',
                   table_id = 'etf_curr',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

etf_major = scraper(url = "https://in.investing.com/etfs/",
                   table_class = 'genTbl closedTbl crossRatesTbl elpTbl elp40',
                   table_id = 'etf_major',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

equity_fund = scraper(url = "https://in.investing.com/funds/",
                   table_class = 'genTbl closedTbl crossRatesTbl elpTbl elp40',
                   table_id = 'fund_eq',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

commodity_fund = scraper(url = "https://in.investing.com/funds/",
                   table_class = 'genTbl closedTbl crossRatesTbl elpTbl elp40',
                   table_id = 'fund_comm',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

bond_fund = scraper(url = "https://in.investing.com/funds/",
                   table_class = 'genTbl closedTbl crossRatesTbl elpTbl elp40',
                   table_id = 'fund_bond',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

major_fund = scraper(url = "https://in.investing.com/funds/",
                   table_class = 'genTbl closedTbl crossRatesTbl elpTbl elp40',
                   table_id = 'fund_major',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

indian_bond = scraper(url = "https://in.investing.com/rates-bonds/",
                   table_class = 'genTbl closedTbl crossRatesTbl',
                   table_id = 'rates_bonds_table_14',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

american_bond = scraper(url = "https://in.investing.com/rates-bonds/",
                   table_class = 'genTbl closedTbl crossRatesTbl',
                   table_id = 'rates_bonds_table_false',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

european_bond = scraper(url = "https://in.investing.com/rates-bonds/",
                   table_class = 'genTbl closedTbl crossRatesTbl',
                   table_id = 'rates_bonds_table_false',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

asia_pacific_bond = scraper(url = "https://in.investing.com/rates-bonds/",
                   table_class = 'genTbl closedTbl crossRatesTbl',
                   table_id = 'rates_bonds_table_false',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

bond_indices = scraper(url = "https://in.investing.com/rates-bonds/",
                   table_class = 'genTbl closedTbl crossRatesTbl',
                   table_id = 'bonds_indices_table',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)

financial_futures = scraper(url = "https://in.investing.com/rates-bonds/",
                   table_class = 'genTbl closedTbl crossRatesTbl',
                   table_id = 'rates_bonds_table_false',
                   start_date = "10/06/2017",
                   response = "Yes Bank",
                   table_filter = False)


#Merge All IVS with DV
data = pd.merge(dv_table,right=currency, how='left', on ='Date')
data = pd.merge(data,right=energy, how='left', on ='Date')
data = pd.merge(data,right=metals, how='left', on ='Date')
data = pd.merge(data,right=agriculture, how='left', on ='Date')
data = pd.merge(data,right=commodities_indices, how='left', on ='Date')
data = pd.merge(data,right=india_indice, how='left', on ='Date')
data = pd.merge(data,right=eu_indice, how='left', on ='Date')
data = pd.merge(data,right=america_indice, how='left', on ='Date')
data = pd.merge(data,right=asia_pacific_indice, how='left', on ='Date')
data = pd.merge(data,right=niftybank, how='left', on ='Date')
data = pd.merge(data,right=etf_equity, how='left', on ='Date')
data = pd.merge(data,right=etf_comm, how='left', on ='Date')
data = pd.merge(data,right=etf_curr, how='left', on ='Date')
data = pd.merge(data,right=etf_major, how='left', on ='Date')
data = pd.merge(data,right=equity_fund, how='left', on ='Date')
data = pd.merge(data,right=commodity_fund, how='left', on ='Date')
data = pd.merge(data,right=bond_fund, how='left', on ='Date')
data = pd.merge(data,right=major_fund, how='left', on ='Date')
data = pd.merge(data,right=indian_bond, how='left', on ='Date')
data = pd.merge(data,right=american_bond, how='left', on ='Date')
data = pd.merge(data,right=european_bond, how='left', on ='Date')
data = pd.merge(data,right=asia_pacific_bond, how='left', on ='Date')
data = pd.merge(data,right=bond_indices, how='left', on ='Date')
data = pd.merge(data,right=financial_futures, how='left', on ='Date')


# Treat Data
def value_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace('B', '')) * 1000000000
    return x

cols = [col for col in data.columns if col not in 'Date']
data2 = data.copy()
data2 = data2.fillna(0)
data2 = data2.replace('-', 0)
for i in cols:
    data2[i] = data2[i].apply(value_to_float)
data2 = data2.drop(data2.std()[(data2.std() == 0)].index, axis=1)    
data2 = data2.replace({'\$': '', ',': ''}, regex=True)
data2.to_csv('data.csv', index = False)

df = pd.read_csv("data_modified.csv")

##########################################################################        
##########################################################################
def get_stock_data(stock_name, out_file_name, from_day, from_month, 
                   from_year, to_day, to_month, to_year):
    
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.support.ui import WebDriverWait as wait
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    import time
    options = Options()
    options.add_experimental_option("prefs", {
      "download.default_directory": r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks",
      "download.prompt_for_download": False,
      "download.directory_upgrade": True,
      "safebrowsing.enabled": True
    })
        
    # url = "https://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?expandable=7&scripcode=532648&flag=sp&Submit=G"
    url = "https://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?scripcode=500247"
    chrome_driver = r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks\chromedriver.exe"
    driver = webdriver.Chrome(chrome_driver,options=options)
    driver.set_page_load_timeout(45)
    driver.get(url)
    time.sleep(1)
    
    driver.find_element_by_id("ContentPlaceHolder1_smartSearch").clear()
    time.sleep(1)
    driver.find_element_by_id("ContentPlaceHolder1_smartSearch").send_keys(stock_name)
    time.sleep(2)
    time.sleep(1)
    drop_down = driver.find_elements_by_css_selector("li.quotemenu a")
    for values in  drop_down:
        values.click()
        break
    #driver.find_element_by_id("ContentPlaceHolder1_smartSearch").click()
    time.sleep(1)
    driver.find_element_by_id("ContentPlaceHolder1_txtFromDate").click()
    time.sleep(1)
    if int(from_year) < 2009:
        mySelect = Select(driver.find_element_by_class_name("ui-datepicker-year"))
        time.sleep(1)
        mySelect.select_by_visible_text("2009")
        time.sleep(1)
    mySelect = Select(driver.find_element_by_class_name("ui-datepicker-year"))
    time.sleep(1)
    mySelect.select_by_visible_text(from_year)
    mySelect = Select(driver.find_element_by_class_name("ui-datepicker-month"))
    mySelect.select_by_visible_text(from_month)
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//td[@data-handler='selectDay']/a[text()='{}']".format(from_day)))).click()
    time.sleep(1)
    
    driver.find_element_by_id("ContentPlaceHolder1_txtToDate").click()
    time.sleep(1)
    if int(to_year) < 2009:
        mySelect = Select(driver.find_element_by_class_name("ui-datepicker-year"))
        time.sleep(1)
        mySelect.select_by_visible_text("2009")
        time.sleep(1)
    mySelect = Select(driver.find_element_by_class_name("ui-datepicker-year"))
    time.sleep(1)
    mySelect.select_by_visible_text(to_year)
    time.sleep(1)
    mySelect = Select(driver.find_element_by_class_name("ui-datepicker-month"))
    mySelect.select_by_visible_text(to_month)
    wait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//td[@data-handler='selectDay']/a[text()='{}']".format(to_day)))).click()
    time.sleep(1)
    
    driver.find_element_by_id('ContentPlaceHolder1_btnSubmit').click()
    time.sleep(2)
    driver.find_element_by_id('ContentPlaceHolder1_btnDownload').click()
    time.sleep(2)
    driver.quit()
    
    import os
    import shutil
    
    path = r"C:\Users\kbhandari\OneDrive - Epsilon\Desktop\Stocks"
    os.chdir(path)
    filename = max([f for f in os.listdir(path)], key=os.path.getctime)
    shutil.move(os.path.join(path,filename),out_file_name)
    return True


get_stock_data(stock_name = "KOTAKBANK", out_file_name = "KOTAK.csv", 
               from_day = "3", from_month = "Jan", from_year = "2005", 
               to_day = "19", to_month = "Jul", to_year = "2019")

get_stock_data(stock_name = "YESBANK", out_file_name = "YESBANK.csv", 
               from_day = "3", from_month = "Jan", from_year = "2005", 
               to_day = "22", to_month = "Jul", to_year = "2019")

get_stock_data(stock_name = "HDFC BANK", out_file_name = "HDFC_BANK.csv", 
               from_day = "3", from_month = "Jan", from_year = "2005", 
               to_day = "19", to_month = "Jul", to_year = "2019")

get_stock_data(stock_name = "SBI", out_file_name = "SBI.csv", 
               from_day = "3", from_month = "Jan", from_year = "2005", 
               to_day = "19", to_month = "Jul", to_year = "2019")