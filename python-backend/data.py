# Import all the necessary modules
import json
import os
import time
import threading
import pytz
import requests # Version: 2.31.0
from dotenv import load_dotenv # Version: 1.0.0
import mysql.connector # Version: 8.2.0
from mysql.connector import Error
import datetime
from snownlp import SnowNLP # Version: 0.12.3
import yfinance as yf # Version 0.2.33
from googletrans import Translator # Version 4.0.0rc1
import pandas as pd # Version 2.1.4
import schedule # Version 1.2.1
import logging
from flask import Flask, jsonify, request # Version 3.0.0
app = Flask(__name__) # initialize flask app at beginning

# Load environmental variables from .env file within python-backend
load_dotenv()
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

finmind_key = os.getenv('FINMIND_KEY')

# String for creating table
create_currentpricetable = """
CREATE TABLE IF NOT EXISTS currentprice(
    symbol VARCHAR(10) NOT NULL,
    datetime DATETIME NOT NULL,
    price FLOAT,
    PRIMARY KEY (symbol, datetime)
);
"""
create_newstable = """
CREATE TABLE IF NOT EXISTS newsarticles (
    article_id VARCHAR(50) NOT NULL,
    pubdate DATETIME,
    title VARCHAR(255) NOT NULL,
    link VARCHAR(1000) NOT NULL,
    creator VARCHAR(50),
    keywords VARCHAR(50),
    image_url VARCHAR(1000),
    source_id VARCHAR(100),
    country VARCHAR(50),
    category VARCHAR(50),
    language VARCHAR(50),
    description VARCHAR(750),
    content TEXT,
    PRIMARY KEY (article_id)
)
"""
create_stocktable = """
CREATE TABLE IF NOT EXISTS stocks (
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    shortname VARCHAR(50),
    longname VARCHAR(100),
    english_name VARCHAR(100),
    businesssummary TEXT,
    longbusinesssummary TEXT,
    exchange VARCHAR(25),
    country VARCHAR(50),
    website VARCHAR(1000),
    address VARCHAR(500),
    english_address VARCHAR(500),
    zip VARCHAR(100),
    sector VARCHAR(500),
    industry VARCHAR(500),
    industrykey VARCHAR(500),
    email VARCHAR(100),
    phone VARCHAR(500),
    fax VARCHAR(500),
    chairman VARCHAR(500),
    ceo VARCHAR(500),
    spokesperson VARCHAR(500),
    acting_spokesperson VARCHAR(500),
    currentprice FLOAT,
    dayhigh FLOAT,
    daylow FLOAT,
    volume BIGINT,
    regularmarketvolume BIGINT,
    marketcap BIGINT,
    enterprisevalue BIGINT,
    trailingpe FLOAT,
    forwardpe FLOAT,
    fiftytwoweeklow FLOAT,
    fiftytwoweekhigh FLOAT,
    PRIMARY KEY (symbol)
)
"""
create_balancesheettable = """
CREATE TABLE IF NOT EXISTS balancesheets(
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    cashandcashequivalents FLOAT,
    cashandcashequivalents_per FLOAT,
    currentfinancialassetsatfairvaluethroughprofitorloss FLOAT,
    currentfinancialassetsatfairvaluethroughprofitorloss_per FLOAT,
    currentfinancialassetsatfairvaluethroughotherincome FLOAT,
    currentfinancialassetsatfairvaluethroughotherincome_per FLOAT,
    financialassetsatamortizedcostnoncurrent FLOAT,
    financialassetsatamortizedcostnoncurrent_per FLOAT,
    otherreceivable FLOAT,
    otherreceivable_per FLOAT,
    accountsreceivablenet FLOAT,
    accountsreceivablenet_per FLOAT,
    inventories FLOAT,
    inventories_per FLOAT,
    othercurrentassets FLOAT,
    othercurrentassets_per FLOAT,
    investmentaccountedforusingequitymethod FLOAT,
    investmentaccountedforusingequitymethod_per FLOAT,
    propertyplantandequipment FLOAT,
    propertyplantandequipment_per FLOAT,
    rightofuseasset FLOAT,
    rightofuseasset_per FLOAT,
    intangibleassets FLOAT,
    intangibleassets_per FLOAT,
    deferredtaxassets FLOAT,
    deferredtaxassets_per FLOAT,
    othernoncurrentassets FLOAT,
    othernoncurrentassets_per FLOAT,
    noncurrentassets FLOAT,
    noncurrentassets_per FLOAT,
    totalassets FLOAT,
    totalassets_per FLOAT,
    shorttermborrowings FLOAT,
    shorttermborrowings_per FLOAT,
    accountspayable FLOAT,
    accountspayable_per FLOAT,
    otherpayables FLOAT,
    otherpayables_per FLOAT,
    currenttaxliabilities FLOAT,
    currenttaxliabilities_per FLOAT,
    PRIMARY KEY (symbol, date)
    );
"""
create_cashflowtable = f"""
CREATE TABLE IF NOT EXISTS cashflow (
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    cashbalancesincrease FLOAT,
    cashflowsfromoperatingactivities FLOAT,
    cashflowsprovidedfromfinancingactivities FLOAT,
    cashbalancesbeginningofperiod FLOAT,
    cashbalancesendofperiod FLOAT,
    netincomebeforetax FLOAT,
    depreciation FLOAT,
    amortizationexpense FLOAT,
    interestexpense FLOAT,
    interestincome FLOAT,
    receivableincrease FLOAT,
    inventoryincrease FLOAT,
    accountspayable FLOAT,
    otherinvestingactivities FLOAT,
    othernoncurrentliabilitiesincrease FLOAT,
    PRIMARY KEY (symbol, date)
    );
"""
create_financialstatements = f"""
CREATE TABLE IF NOT EXISTS financialstatements (
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    revenue FLOAT,
    costsofgoodssold FLOAT,
    grossprofit FLOAT,
    operatingexpenses FLOAT,
    operatingincome FLOAT,
    totalnonoperatingincomeandexpense FLOAT,
    pretaxincome FLOAT,
    incomefromcontinuingoperations FLOAT,
    incomeaftertaxes FLOAT,
    totalconsolidatedprofitfortheperiod FLOAT,
    eps FLOAT,
    equityattributabletoownersofparent FLOAT,
    noncontrollinginterests FLOAT,
    othercomprehensiveincome FLOAT,
    PRIMARY KEY (symbol, date)
    );
"""
create_stockprices = f"""
CREATE TABLE IF NOT EXISTS stockprices (
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    trading_volume BIGINT,
    trading_money BIGINT,
    open FLOAT,
    max FLOAT,
    min FLOAT,
    close FLOAT,
    spread FLOAT,
    trading_turnover BIGINT,
    PRIMARY KEY (symbol, date)
    );
"""
create_dividendrates = f"""
CREATE TABLE IF NOT EXISTS dividendrates (
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    dividendrate FLOAT,
    dividendyield FLOAT,
    exdividenddate DATE,
    fiveyearavgdividendyield FLOAT,
    trailingannualdividendrate FLOAT,
    trailingannualdividendyield FLOAT,
    lastdividendvalue FLOAT,
    lastdividenddate DATE,
    PRIMARY KEY (symbol)
    );
"""
create_marketindex = f"""
CREATE TABLE IF NOT EXISTS marketindex (
    index_symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    adj_close FLOAT,
    volume BIGINT,
    PRIMARY KEY (index_symbol, date)
);
"""
# Method for connecting to mySQL database
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            passwd = user_password,
            database = db_name
        )
        print("Connection to MySQL DB successful!")
        logging.info('Connection to MySQL DB successful!')
    except Error as e:
        print(f"Error {e} during connection to database")
        logging.error(f"Error {e} occurred during connection to MySQL database")
    return connection

# Method for executing SQL queries
def execute_query(connection, query, params = None):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        print("Query execution successful!")
    except Error as e:
        print(f"The error {e} occurred during query execution")
        logging.error(f"The error {e} occurred during query execution")

# Method for reading a specific table from within the database
def execute_read_query(connection, table, query = None):
    cursor = connection.cursor(dictionary=True)
    result = None
    if query == None:
        query = f"SELECT * FROM {table};" # initialize SELECT ALL query
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred during reading")
        logging.error(f"The error '{e}' occurred during reading")

# Method for translating text using googletrans
def translate_text(text, target_language = 'zh-tw'):
    translator = Translator()
    translation = translator.translate(text, dest = target_language)
    return translation.text

# Method for retrieving news articles
def retrieve_news(page = ''):
    url = "https://newsdata.io/api/1/news"
    p = {
            'country':'tw',
            'category':'business',
            'apikey':'pub_3600720b45e20e8aff24d831f67217c911fe3'
        }
    if page != '':
        p['page'] = page
    response = requests.get(url, params = p)
    raw = response.json()
    if raw['status'] == "error":
        status = {'status':raw['status'], 'message':raw['results']['message'], 'code':raw['results']['code']} # return dictionary
        return status, None, None
    else:
        status = {'status':'success', 'message':None, 'code':None} # return dictionary
        nextpage = raw['nextPage']
        news = raw['results']
        return status, news, nextpage

# Method to run everyday in order to update news (run once every 10 min)
def update_news(connection):
    print("Retrieving latest Taiwanese business news articles")
    logging.info("Retrieving latest Taiwanese business news articles")
    # Retrieve all 公司簡稱 names into a list
    stock_names = [entry['shortname'] for entry in execute_read_query(connection, "stocks", "SELECT shortname FROM stocks;")]
    
    nextpage = ''
    news_database = execute_read_query(connection, "newsarticles")
    article_id_ls = [value for entry in news_database for key, value in entry.items() if key == 'article_id']
    article_id_set = set(article_id_ls) # generate set of article_ids (database)
    # Check the news API 20 iterations each time
    for i in range(20):
        status, news, nextpage = retrieve_news(nextpage)
        if status['status'] == 'error': # exit if error occurs
            print(f"News API call error:\nMessage:{status['message']}\nCode:{status['code']}")
            logging.info(f"News API call error:\nMessage:{status['message']}\nCode:{status['code']}")
            break
        news_id_ls = [value for entry in news for key, value in entry.items() if key == 'article_id']
        news_id_set = set(news_id_ls) # generate set of article_ids (api call)
        new_news = list(news_id_set - article_id_set)
        news_data = [entry for entry in news for key, value in entry.items() if key == 'article_id' and value in new_news]
        for entry in news_data:
            if entry['content'] == None or entry['article_id'] == None: # if one of these does not exist, do not proceed into loop
                break
            for key, value in entry.items():
                if key == 'article_id':
                    article_id = value
                elif key == 'pubDate':
                    pubdate = str(value) # ensure that datetime is converted to string
                elif key == 'title':
                    title = value
                elif key == 'link':
                    link = value
                elif key == 'creator':
                    if isinstance(value, list):
                        creator = ', '.join(value) # convert to string
                    else:
                        creator = value
                elif key == 'keywords':
                    if isinstance(value, list):
                        keywords = ', '.join(value)
                    else: # If keywords is empty, search for keywords yourself
                        keywords_ls = [value] if value else []
                        for name in stock_names:
                            if name in entry['content']:
                                keywords_ls.append(name)
                        keywords_set = set(keywords_ls) # remove duplicates
                        keywords_ls = list(keywords_set)
                        keywords = ', '.join(keywords_ls) if keywords_ls else None
                elif key == 'image_url':
                    image_url = value
                elif key == 'source_id':
                    source_id = value
                elif key == 'country':
                    if isinstance(value, list):
                        country = ', '.join(value)
                    else:
                        country = value
                elif key == 'category':
                    if isinstance(value, list):
                        category = ', '.join(value)
                    else:
                        category = value
                elif key == 'language':
                    language = value
                elif key == 'description':
                    description = value
                elif key == 'content':
                    content = value

            # Prepare strings outside the f-string
            title_safe = title.replace("'", "''")
            description_safe = description.replace("'", "''")
            content_safe = content.replace("'", "''")
            s = SnowNLP(content)# Perform sentiment analysis through SnowNLP
            sentiment = round(float(s.sentiments), 3)
            if sentiment == 0.000: # Make sentiment neutral if snowNLP library unable to measure 
                sentiment = 0.500
            # Correct INSERT statement
            insert = f"""
            INSERT INTO newsarticles (article_id, pubdate, title, link, creator, keywords, image_url, source_id, country, category, language, description, content, sentiment)
            VALUES (
                '{article_id}', 
                {f"'{pubdate}'" if pubdate is not None else 'NULL'},
                '{title_safe}', 
                '{link}', 
                {f"'{creator}'" if creator is not None else 'NULL'}, 
                {f"'{keywords}'" if keywords is not None else 'NULL'}, 
                '{image_url}', 
                '{source_id}', 
                {f"'{country}'" if country is not None else 'NULL'}, 
                {f"'{category}'" if category is not None else 'NULL'}, 
                '{language}', 
                '{description_safe}', 
                '{content_safe}',
                '{sentiment}'
            );
            """
            execute_query(connection, insert) # insert values into table
    
# Method to retrieve basic information for API
def retrieve_stocks(url, p = None):
    try:
        response = requests.get(url, params = p)
        data = response.json()
    except json.JSONDecodeError:
        print("Response not in JSON format")
        logging.info("Response not in JSON format")
        print(f"{response}")
        logging.info(f"{response}")
        data = {'status':502, 'msg':'Bad gateway: server seems to be experiencing issues (received invalid response from upstream server)'}
    return data

# Method to run in order to update company basic information (within 'stocks' SQL table)
def update_stocks(connection):
    twse_data = retrieve_stocks("https://openapi.twse.com.tw/v1/opendata/t187ap03_L")
    count = 1
    for stock in twse_data:
        print(f"Updating {count} of {len(twse_data)} for latest stock data")
        logging.info(f"Updating {count} of {len(twse_data)} for latest stock data")
        shortname, longname, english_name, website, address, email, phone, fax, chairman, ceo, spokesperson, acting_spokesperson = None, None, None, None, None, None, None, None, None, None, None, None # Define None types first
        for key in list(stock.keys()):
            if key == '公司代號':
                symbol = str(stock[key].strip())
                symbol_query = str(symbol) + '.TW'
                ystock = yf.Ticker(symbol_query).info
                # Acquire corresponding data from yfinance
                longbusinesssummary = ystock.get('longBusinessSummary', None).replace("'", "''") if ystock.get('longBusinessSummary') else None
                if longbusinesssummary == None:
                    businesssummary = None
                else:
                    yf_longname = ystock.get('longName', None) if ystock.get('longName') else None
                    summary = longbusinesssummary
                exchange = ystock.get('exchange', None).replace("'", "''") if ystock.get('exchange') else None
                country = ystock.get('country', None).replace("'", "''") if ystock.get('country') else None
                english_address = str(ystock.get('address1', '') + ' ' + ystock.get('address2', '')).strip().replace("'", "''") if ystock.get('address1') or ystock.get('address2') else None
                zip = ystock.get('zip', None)
                sector = ystock.get('sector', None).replace("'", "''") if ystock.get('sector') else None
                industry = ystock.get('industry', None).replace("'", "''") if ystock.get('industry') else None
                industrykey = ystock.get('industryKey', None).replace("'", "''") if ystock.get('industryKey') else None
                currentprice = float(ystock.get('currentPrice', None)) if ystock.get('currentPrice') else None
                dayhigh = float(ystock.get('dayHigh', None)) if ystock.get('dayHigh') else None
                daylow = float(ystock.get('dayLow', None)) if ystock.get('dayLow') else None
                volume = int(ystock.get('volume', None)) if ystock.get('volume') else None
                regularmarketvolume = int(ystock.get('regularMarketVolume', None)) if ystock.get('regularMarketVolume') else None
                marketcap = int(ystock.get('marketCap', None)) if ystock.get('marketCap') else None
                enterprisevalue = int(ystock.get('enterpriseValue', None)) if ystock.get('enterpriseValue') else None
                trailingpe = float(ystock.get('trailingPE', None)) if ystock.get('trailingPE') else None
                forwardpe = float(ystock.get('forwardPE', None)) if ystock.get('forwardPE') else None
                fiftytwoweeklow = float(ystock.get('fiftyTwoWeekLow', None)) if ystock.get('fiftyTwoWeekLow') else None
                fiftytwoweekhigh = float(ystock.get('fiftyTwoWeekHigh', None)) if ystock.get('fiftyTwoWeekHigh') else None

            elif key == '出表日期':
                year = str(int(stock[key][:3]) + 1911)
                month = stock[key][3:5]
                day = stock[key][5:]
                date = f"{year}-{month}-{day}"
            elif key == '公司簡稱':
                shortname = stock[key].replace("'", "''")
                if longbusinesssummary != None:
                    summary_modified = summary.replace(yf_longname, shortname)
                    businesssummary = translate_text(summary_modified).replace("'", "''")# Translate for chinese businesssummary
            elif key == '公司名稱':
                longname = stock[key].replace("'", "''")
            elif key == '英文簡稱':
                english_name = stock[key].strip().replace("'", "''")
            elif key == '網址':
                website = stock[key].strip()
            elif key == '住址':
                address = stock[key].strip().replace("'", "''")
            elif key == '電子郵件信箱':
                email = stock[key].strip()
            elif key == '總機電話':
                phone = stock[key].strip()
            elif key == '傳真機號碼':
                fax = stock[key].strip()
            elif key == '董事長':
                chairman = stock[key].strip().replace("'", "''")
            elif key == '總經理':
                ceo = stock[key].strip().replace("'", "''")
            elif key == '發言人':
                spokesperson = stock[key].strip().replace("'", "''")
            elif key == '代理發言人':
                acting_spokesperson = stock[key].strip().replace("'", "''")
        insert = f"""
        INSERT INTO stocks (
            symbol, date, shortname, longname, english_name, businesssummary, longbusinesssummary, exchange, country, website, address, english_address, zip, sector, industry, industrykey, email, phone, fax, chairman, ceo, spokesperson, acting_spokesperson, currentprice, dayhigh, daylow, volume, regularmarketvolume, marketcap, enterprisevalue, trailingpe, forwardpe, fiftytwoweeklow, fiftytwoweekhigh
        ) VALUES (
            '{symbol}', 
            '{date}',
            {f"'{shortname}'" if shortname else 'NULL'},
            {f"'{longname}'" if longname else 'NULL'},
            {f"'{english_name}'" if english_name else 'NULL'},
            {f"'{businesssummary}'" if businesssummary else 'NULL'},
            {f"'{longbusinesssummary}'" if longbusinesssummary else 'NULL'},
            {f"'{exchange}'" if exchange else 'NULL'},
            {f"'{country}'" if country else 'NULL'},
            {f"'{website}'" if website else 'NULL'},
            {f"'{address}'" if address else 'NULL'},
            {f"'{english_address}'" if english_address else 'NULL'},
            {f"'{zip}'" if zip else 'NULL'},
            {f"'{sector}'" if sector else 'NULL'},
            {f"'{industry}'" if industry else 'NULL'},
            {f"'{industrykey}'" if industrykey else 'NULL'},
            {f"'{email}'" if email else 'NULL'},
            {f"'{phone}'" if phone else 'NULL'},
            {f"'{fax}'" if fax else 'NULL'},
            {f"'{chairman}'" if chairman else 'NULL'},
            {f"'{ceo}'" if ceo else 'NULL'},
            {f"'{spokesperson}'" if spokesperson else 'NULL'},
            {f"'{acting_spokesperson}'" if acting_spokesperson else 'NULL'},
            {currentprice if currentprice is not None else 'NULL'},
            {dayhigh if dayhigh is not None else 'NULL'},
            {daylow if daylow is not None else 'NULL'},
            {volume if volume is not None else 'NULL'},
            {regularmarketvolume if regularmarketvolume is not None else 'NULL'},
            {marketcap if marketcap is not None else 'NULL'},
            {enterprisevalue if enterprisevalue is not None else 'NULL'},
            {trailingpe if trailingpe is not None else 'NULL'},
            {forwardpe if forwardpe is not None else 'NULL'},
            {fiftytwoweeklow if fiftytwoweeklow is not None else 'NULL'},
            {fiftytwoweekhigh if fiftytwoweekhigh is not None else 'NULL'}
        )
        ON DUPLICATE KEY UPDATE
            date = VALUES(date),
            shortname = VALUES(shortname),
            longname = VALUES(longname),
            english_name = VALUES(english_name),
            businesssummary = VALUES(businesssummary),
            longbusinesssummary = VALUES(longbusinesssummary),
            exchange = VALUES(exchange),
            country = VALUES(country),
            website = VALUES(website),
            address = VALUES(address),
            english_address = VALUES(english_address),
            zip = VALUES(zip),
            sector = VALUES(sector),
            industry = VALUES(industry),
            industrykey = VALUES(industrykey),
            email = VALUES(email),
            phone = VALUES(phone),
            fax = VALUES(fax),
            chairman = VALUES(chairman),
            ceo = VALUES(ceo),
            spokesperson = VALUES(spokesperson),
            acting_spokesperson = VALUES(acting_spokesperson),
            currentprice = VALUES(currentprice),
            dayhigh = VALUES(dayhigh),
            daylow = VALUES(daylow),
            volume = VALUES(volume),
            regularmarketvolume = VALUES(regularmarketvolume),
            marketcap = VALUES(marketcap),
            enterprisevalue = VALUES(enterprisevalue),
            trailingpe = VALUES(trailingpe),
            forwardpe = VALUES(forwardpe),
            fiftytwoweeklow = VALUES(fiftytwoweeklow),
            fiftytwoweekhigh = VALUES(fiftytwoweekhigh);
        """
        execute_query(connection, insert)
        count += 1

# Method to retrieve balancesheet
def update_financials(connection, dataset, columns_list, insert_sql):
    reference_dict = {'TaiwanStockBalanceSheet':'balancesheets', 'TaiwanStockCashFlowsStatement':'cashflow', 'TaiwanStockFinancialStatements':'financialstatements', 'TaiwanStockPrice':'stockprices'}
    print(f"Entering update financials {dataset} for table {reference_dict[dataset]}")
    logging.info(f"Entering update financials {dataset} for table {reference_dict[dataset]}")
    duplicate = execute_read_query(connection, reference_dict[dataset], f"SELECT symbol, date FROM {reference_dict[dataset]}")
    duplicate_dict = {} # For storing key-value pair duplicates (e.g. '1101':['2023-09-31', '2024-04-30', ....], ...)
    duplicate_symbol = list(set([entry['symbol'] for entry in duplicate])) # all unique entries of stock symbols
    for symbol in duplicate_symbol:
        date_ls = [] # storing dates
        for row in duplicate:
            if row['symbol'] == symbol:
                date_ls.append(str(row['date'])) # convert datetime object (SQL) to string (e.g. '1920-01-01')
        duplicate_dict[symbol] = date_ls

    print(f"Running dataset {dataset}")
    logging.info(f"Running dataset {dataset}")
    stock_ls = [entry['symbol'] for entry in execute_read_query(connection, "stocks", "SELECT symbol FROM stocks;")]
    count = 1
    max_retries = 5 # set maximum retries
    retry_delay = 13 # in minutes
    for stock in stock_ls:
        status = 402
        retries = 0
        while (status == 402 or status == 502) and retries < max_retries: # if msg request failed and retries < max_retries
            print(f"Retrieving {count} of {len(stock_ls)}, symbol: {stock} ({reference_dict[dataset]} table)")
            logging.info(f"Retrieving {count} of {len(stock_ls)}, symbol: {stock} ({reference_dict[dataset]} table)")
            url = "https://api.finmindtrade.com/api/v4/data"
            param = {
                'dataset':dataset,
                'data_id':stock,
                'start_date':'1990-01-01',
                'token':finmind_key
            }
            balance_data = retrieve_stocks(url, param)
            status = balance_data.get('status')
            msg = balance_data.get('msg')
            if status == 200:
                break
            print(f"Retrieval failed\nStatus:{status} Msg:{msg}\nRetrying again in {retry_delay} minutes")
            logging.info(f"Retrieval failed\nStatus:{status} Msg:{msg}\nRetrying again in {retry_delay} minutes")
            time.sleep(retry_delay*60)
            retries += 1
        else:
            raise Exception("Retrieval of balance sheet data failed even after max retries have been reached")

        figures = {type.lower():None for type in columns_list} # initialize empty dictionary
        # Writing the values into variables
        balance_sheet = balance_data['data']
        date_dict = {} # initialize empty dictionary (date:{figures}, date:{figures...})
        for entry in balance_sheet:
            date = entry['date']
            for key, value in entry.items():
                if key == 'type':
                    if value in columns_list:
                        type = value.lower()
                        figures[type] = float(entry['value'])
            date_dict[date] = figures # set key-value pair for dictionary
        # Remove duplicate entries
        for key in list(date_dict.keys()):
            if duplicate_dict.get(stock) != None:
                if key in duplicate_dict[stock]:
                    date_dict.pop(key)
        # Arrange the tuples in order (date_dict is emtpy if all are duplicates)
        for date in list(date_dict.keys()):
            key_tuple = (stock, date) # stock = symbol & key = date
            value_ls = []
            for column in columns_list:
                for key, value in date_dict[date].items():
                    if key == column.lower():
                        value_ls.append(value)
            value_tuple = tuple(value_ls)
            output_tuple = key_tuple + value_tuple # create larger tuple list
            execute_query(connection, insert_sql, output_tuple)
        # Next stock
        count += 1

# Method for converting unix timestamps into the format YYYY-MM-DD
def convert_unix_timestamp(unix_timestamp):
    if unix_timestamp == None:
        return None
    else:
        timestamp_datetime = datetime.datetime.utcfromtimestamp(unix_timestamp)
        formatted_date = timestamp_datetime.strftime('%Y-%m-%d')
        return formatted_date
# Method for retrieving dividends for each stock
def update_dividends(connection):
    print(f"Updating dividend rates (daily update)")
    logging.info(f"Updating dividend rates (daily update)")
    stocks_data = execute_read_query(connection, 'stocks', 'SELECT symbol FROM stocks;')
    symbol_ls = [stock['symbol'] for stock in stocks_data]
    date = datetime.datetime.now().strftime('%Y-%m-%d') # get current date
    count = 1
    for symbol in symbol_ls:
        print(f"Updating dividend rates {count} out of {len(symbol_ls)} for {symbol}")
        logging.info(f"Updating dividend rates {count} out of {len(symbol_ls)} for {symbol}")
        symbol_TW = symbol + '.TW'
        stock = yf.Ticker(symbol_TW).info # stock is a dictionary (keys: address1, address2)
        dividendrate = stock['dividendRate'] if stock.get('dividendRate') else None
        dividendyield = stock['dividendYield'] if stock.get('dividendYield') else None
        exdividenddate = convert_unix_timestamp(stock['exDividendDate'] if stock.get('exDividendDate') else None)
        fiveyearavgdividendyield = stock['fiveYearAvgDividendYield'] if stock.get('fiveYearAvgDividendYield') else None
        trailingannualdividendrate = stock['trailingAnnualDividendRate'] if stock.get('trailingAnnualDividendRate') else None
        trailingannualdividendyield = stock['trailingAnnualDividendYield'] if stock.get('trailingAnnualDividendYield') else None
        lastdividendvalue = stock['lastDividendValue'] if stock.get('lastDividendValue') else None
        lastdividenddate = convert_unix_timestamp(stock['lastDividendDate'] if stock.get('lastDividendDate') else None)
        output_tuple = (symbol, date, dividendrate, dividendyield, exdividenddate, fiveyearavgdividendyield, trailingannualdividendrate, trailingannualdividendyield, lastdividendvalue, lastdividenddate)
        insert_sql = f"""
        INSERT INTO dividendrates (
            symbol, date, dividendrate, dividendyield, exdividenddate, fiveyearavgdividendyield,
            trailingannualdividendrate, trailingannualdividendyield, lastdividendvalue, lastdividenddate
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON DUPLICATE KEY UPDATE
            date = VALUES(date),
            dividendrate = VALUES(dividendrate),
            dividendyield = VALUES(dividendyield),
            exdividenddate = VALUES(exdividenddate),
            fiveyearavgdividendyield = VALUES(fiveyearavgdividendyield),
            trailingannualdividendrate = VALUES(trailingannualdividendrate),
            trailingannualdividendyield = VALUES(trailingannualdividendyield),
            lastdividendvalue = VALUES(lastdividendvalue),
            lastdividenddate = VALUES(lastdividenddate);
        """
        execute_query(connection, insert_sql, output_tuple)
        count += 1

# Method for updating market index data
def update_index(connection):
    print("Updating market indexes...")
    logging.info("Updating market indexes...")
    index_data = [entry for entry in execute_read_query(connection, 'marketindex', 'SELECT index_symbol, date FROM marketindex;')] # list of dictionaries
    index_ls = list(set([entry['index_symbol'] for entry in index_data]))
    reference_dict = {} # initialize dictionary ('^DJI':['2024-01-02', '2024-01-03'...], '^GSPC':)
    for index in index_ls:
        date_ls = []
        for row in index_data:
            if row['index_symbol'] == index:
                date_ls.append(str(row['date']))
        reference_dict[index] = date_ls
    market_indexes = ['^DJI', '^GSPC', '^N225', '^HSI', '^TWII', '^IXIC']
    count = 1
    for entry in market_indexes:
        print(f"Updating market index: {entry} Count {count} of {len(market_indexes)}")
        logging.info(f"Updating market index: {entry} Count {count} of {len(market_indexes)}")
        market_index = yf.download(entry) # pandas dataframe
        date_index = [date.strftime('%Y-%m-%d') for date in list(market_index.index)] # list of all dates within dataframe      
        duplicate_dict = {} # initialize dictionary ('2024-01-01':[list of values], '2024-01-02':[list of values] (in order), ...)
        for date in date_index:
            data = market_index.loc[date]
            open = float(data['Open']) if not pd.isna(data['Open']) else None
            high = float(data['High']) if not pd.isna(data['High']) else None
            low = float(data['Low']) if not pd.isna(data['Low']) else None
            close = float(data['Close']) if not pd.isna(data['Close']) else None
            adj_close = float(data['Adj Close']) if not pd.isna(data['Adj Close']) else None
            volume = int(data['Volume']) if not pd.isna(data['Volume']) else None
            ls = [open, high, low, close, adj_close, volume] # put everything into list (in order)
            duplicate_dict[date] = ls
        # Remove duplicate entries
        for duplicate_date in list(duplicate_dict.keys()):
            if reference_dict.get(entry) != None: # Make sure that key exists first
                if duplicate_date in reference_dict[entry]:
                    duplicate_dict.pop(duplicate_date)
        for key in list(duplicate_dict.keys()): # key is date
            key_tuple = (entry, key) # (index_symbol, date)
            output_tuple = key_tuple + tuple(duplicate_dict[key])
            insert_sql = f"""
            INSERT INTO marketindex (
                index_symbol, date, open, high, low, close, adj_close, volume
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE
                open = COALESCE(VALUES(open), open),
                high = COALESCE(VALUES(high), high),
                low = COALESCE(VALUES(low), low),
                close = COALESCE(VALUES(close), close),
                adj_close = COALESCE(VALUES(adj_close), adj_close),
                volume = COALESCE(VALUES(volume), volume);
            """
            execute_query(connection, insert_sql, output_tuple)
        count += 1

# Method to update currentprice table
def update_currentprice(connection, interval = 5):
    print(f"Updating current price (in {interval} minute intervals)")
    logging.info(f"Updating current price (in {interval} minute intervals)")
    stocks_data = execute_read_query(connection, 'stocks', 'SELECT symbol FROM stocks;')
    symbol_ls = [stock['symbol'] for stock in stocks_data]
    count = 1
    for symbol in symbol_ls:
        print(f"Updating {symbol}: Count {count} of {len(symbol_ls)}")
        logging.info(f"Updating {symbol}: Count {count} of {len(symbol_ls)}")
        sql_query = f"SELECT datetime, price FROM currentprice WHERE symbol = '{symbol}';"
        stock_data = execute_read_query(connection, 'currentprice', sql_query) # list of dictionaries
        if stock_data != None and len(stock_data) >= 1674: # this number because 54 entries a day (market open to close) and 31 days per month
            # delete the earliest entry for the stock
            sql_delete = f"""
            DELETE FROM currentprice
            WHERE symbol = '{symbol}'
            ORDER BY datetime
            LIMIT 1;
            """
            execute_query(connection, sql_delete)
        # get current datetime
        current_datetime = datetime.datetime.now()
        # Get current market price for stock
        yf_query = symbol + '.TW'
        stock = yf.Ticker(yf_query).info
        price = stock.get('currentPrice')
        insert_sql = f"""
        INSERT INTO currentprice (
            symbol, datetime, price
        ) VALUES (
            %s, %s, %s
        );
        """
        # construct output tuple
        output_tuple = (symbol, current_datetime, price)
        # insert into table
        execute_query(connection, insert_sql, output_tuple)
        count += 1

# For financials (balancesheet, cashflow and financialstatement)
# Columns list
columns_list_balancesheet = [
    'CashAndCashEquivalents',
    'CashAndCashEquivalents_per',
    'CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss',
    'CurrentFinancialAssetsAtFairvalueThroughProfitOrLoss_per',
    'CurrentFinancialAssetsAtFairvalueThroughOtherIncome',
    'CurrentFinancialAssetsAtFairvalueThroughOtherIncome_per',
    'FinancialAssetsAtAmortizedCostNonCurrent',
    'FinancialAssetsAtAmortizedCostNonCurrent_per',
    'OtherReceivable',
    'OtherReceivable_per',
    'AccountsReceivableNet',
    'AccountsReceivableNet_per',
    'Inventories',
    'Inventories_per',
    'OtherCurrentAssets',
    'OtherCurrentAssets_per',
    'InvestmentAccountedForUsingEquityMethod',
    'InvestmentAccountedForUsingEquityMethod_per',
    'PropertyPlantAndEquipment',
    'PropertyPlantAndEquipment_per',
    'RightOfUseAsset',
    'RightOfUseAsset_per',
    'IntangibleAssets',
    'IntangibleAssets_per',
    'DeferredTaxAssets',
    'DeferredTaxAssets_per',
    'OtherNoncurrentAssets',
    'OtherNoncurrentAssets_per',
    'NoncurrentAssets',
    'NoncurrentAssets_per',
    'TotalAssets',
    'TotalAssets_per',
    'ShorttermBorrowings',
    'ShorttermBorrowings_per',
    'AccountsPayable',
    'AccountsPayable_per',
    'OtherPayables',
    'OtherPayables_per',
    'CurrentTaxLiabilities',
    'CurrentTaxLiabilities_per'
]

columns_list_cashflow = [
    'CashBalancesIncrease',
    'CashFlowsFromOperatingActivities',
    'CashFlowsProvidedFromFinancingActivities',
    'CashBalancesBeginningOfPeriod',
    'CashBalancesEndOfPeriod',
    'NetIncomeBeforeTax',
    'Depreciation',
    'AmortizationExpense',
    'InterestExpense',
    'InterestIncome',
    'ReceivableIncrease',
    'InventoryIncrease',
    'AccountsPayable',
    'OtherInvestingActivities',
    'OtherNonCurrentLiabilitiesIncrease'
]

columns_list_financialstatement = [
    'Revenue',
    'CostsOfGoodsSold',
    'GrossProfit',
    'OperatingExpenses',
    'OperatingIncome',
    'TotalNonoperatingIncomeAndExpense',
    'PreTaxIncome',
    'IncomeFromContinuingOperations',
    'IncomeAfterTaxes',
    'TotalConsolidatedProfitForThePeriod',
    'EPS',
    'EquityAttributableToOwnersOfParent',
    'NoncontrollingInterests',
    'OtherComprehensiveIncome'
]

columns_list_stockprice = [
    'Trading_Volume',
    'Trading_money',
    'open', 
    'max',
    'min',
    'close',
    'spread',
    'Trading_turnover'
]
# insert_sql
insert_sql_balancesheet = f"""
INSERT INTO balancesheets (
    symbol, date, cashandcashequivalents, cashandcashequivalents_per,
    currentfinancialassetsatfairvaluethroughprofitorloss, currentfinancialassetsatfairvaluethroughprofitorloss_per,
    currentfinancialassetsatfairvaluethroughotherincome, currentfinancialassetsatfairvaluethroughotherincome_per,
    financialassetsatamortizedcostnoncurrent, financialassetsatamortizedcostnoncurrent_per,
    otherreceivable, otherreceivable_per, accountsreceivablenet, accountsreceivablenet_per,
    inventories, inventories_per, othercurrentassets, othercurrentassets_per,
    investmentaccountedforusingequitymethod, investmentaccountedforusingequitymethod_per,
    propertyplantandequipment, propertyplantandequipment_per, rightofuseasset, rightofuseasset_per,
    intangibleassets, intangibleassets_per, deferredtaxassets, deferredtaxassets_per,
    othernoncurrentassets, othernoncurrentassets_per, noncurrentassets, noncurrentassets_per,
    totalassets, totalassets_per, shorttermborrowings, shorttermborrowings_per,
    accountspayable, accountspayable_per, otherpayables, otherpayables_per,
    currenttaxliabilities, currenttaxliabilities_per
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s
) ON DUPLICATE KEY UPDATE
    cashandcashequivalents = COALESCE(VALUES(cashandcashequivalents), cashandcashequivalents),
    cashandcashequivalents_per = COALESCE(VALUES(cashandcashequivalents_per), cashandcashequivalents_per),
    currentfinancialassetsatfairvaluethroughprofitorloss = COALESCE(VALUES(currentfinancialassetsatfairvaluethroughprofitorloss), currentfinancialassetsatfairvaluethroughprofitorloss),
    currentfinancialassetsatfairvaluethroughprofitorloss_per = COALESCE(VALUES(currentfinancialassetsatfairvaluethroughprofitorloss_per), currentfinancialassetsatfairvaluethroughprofitorloss_per),
    currentfinancialassetsatfairvaluethroughotherincome = COALESCE(VALUES(currentfinancialassetsatfairvaluethroughotherincome), currentfinancialassetsatfairvaluethroughotherincome),
    currentfinancialassetsatfairvaluethroughotherincome_per = COALESCE(VALUES(currentfinancialassetsatfairvaluethroughotherincome_per), currentfinancialassetsatfairvaluethroughotherincome_per),
    financialassetsatamortizedcostnoncurrent = COALESCE(VALUES(financialassetsatamortizedcostnoncurrent), financialassetsatamortizedcostnoncurrent),
    financialassetsatamortizedcostnoncurrent_per = COALESCE(VALUES(financialassetsatamortizedcostnoncurrent_per), financialassetsatamortizedcostnoncurrent_per),
    otherreceivable = COALESCE(VALUES(otherreceivable), otherreceivable),
    otherreceivable_per = COALESCE(VALUES(otherreceivable_per), otherreceivable_per),
    accountsreceivablenet = COALESCE(VALUES(accountsreceivablenet), accountsreceivablenet),
    accountsreceivablenet_per = COALESCE(VALUES(accountsreceivablenet_per), accountsreceivablenet_per),
    inventories = COALESCE(VALUES(inventories), inventories),
    inventories_per = COALESCE(VALUES(inventories_per), inventories_per),
    othercurrentassets = COALESCE(VALUES(othercurrentassets), othercurrentassets),
    othercurrentassets_per = COALESCE(VALUES(othercurrentassets_per), othercurrentassets_per),
    investmentaccountedforusingequitymethod = COALESCE(VALUES(investmentaccountedforusingequitymethod), investmentaccountedforusingequitymethod),
    investmentaccountedforusingequitymethod_per = COALESCE(VALUES(investmentaccountedforusingequitymethod_per), investmentaccountedforusingequitymethod_per),
    propertyplantandequipment = COALESCE(VALUES(propertyplantandequipment), propertyplantandequipment),
    propertyplantandequipment_per = COALESCE(VALUES(propertyplantandequipment_per), propertyplantandequipment_per),
    rightofuseasset = COALESCE(VALUES(rightofuseasset), rightofuseasset),
    rightofuseasset_per = COALESCE(VALUES(rightofuseasset_per), rightofuseasset_per),
    intangibleassets = COALESCE(VALUES(intangibleassets), intangibleassets),
    intangibleassets_per = COALESCE(VALUES(intangibleassets_per), intangibleassets_per),
    deferredtaxassets = COALESCE(VALUES(deferredtaxassets), deferredtaxassets),
    deferredtaxassets_per = COALESCE(VALUES(deferredtaxassets_per), deferredtaxassets_per),
    othernoncurrentassets = COALESCE(VALUES(othernoncurrentassets), othernoncurrentassets),
    othernoncurrentassets_per = COALESCE(VALUES(othernoncurrentassets_per), othernoncurrentassets_per),
    noncurrentassets = COALESCE(VALUES(noncurrentassets), noncurrentassets),
    noncurrentassets_per = COALESCE(VALUES(noncurrentassets_per), noncurrentassets_per),
    totalassets = COALESCE(VALUES(totalassets), totalassets),
    totalassets_per = COALESCE(VALUES(totalassets_per), totalassets_per),
    shorttermborrowings = COALESCE(VALUES(shorttermborrowings), shorttermborrowings),
    shorttermborrowings_per = COALESCE(VALUES(shorttermborrowings_per), shorttermborrowings_per),
    accountspayable = COALESCE(VALUES(accountspayable), accountspayable),
    accountspayable_per = COALESCE(VALUES(accountspayable_per), accountspayable_per),
    otherpayables = COALESCE(VALUES(otherpayables), otherpayables),
    otherpayables_per = COALESCE(VALUES(otherpayables_per), otherpayables_per),
    currenttaxliabilities = COALESCE(VALUES(currenttaxliabilities), currenttaxliabilities),
    currenttaxliabilities_per = COALESCE(VALUES(currenttaxliabilities_per), currenttaxliabilities_per);
"""
insert_sql_cashflow = f"""
INSERT INTO cashflow (
    symbol, date, cashbalancesincrease, cashflowsfromoperatingactivities, cashflowsprovidedfromfinancingactivities, 
    cashbalancesbeginningofperiod, cashbalancesendofperiod, netincomebeforetax, depreciation,
    amortizationexpense, interestexpense, interestincome, receivableincrease,
    inventoryincrease, accountspayable, otherinvestingactivities, othernoncurrentliabilitiesincrease 
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
) ON DUPLICATE KEY UPDATE
    cashbalancesincrease = COALESCE(VALUES(cashbalancesincrease), cashbalancesincrease),
    cashflowsfromoperatingactivities = COALESCE(VALUES(cashflowsfromoperatingactivities), cashflowsfromoperatingactivities),
    cashflowsprovidedfromfinancingactivities = COALESCE(VALUES(cashflowsprovidedfromfinancingactivities), cashflowsprovidedfromfinancingactivities),
    cashbalancesbeginningofperiod = COALESCE(VALUES(cashbalancesbeginningofperiod), cashbalancesbeginningofperiod),
    cashbalancesendofperiod = COALESCE(VALUES(cashbalancesendofperiod), cashbalancesendofperiod),
    netincomebeforetax = COALESCE(VALUES(netincomebeforetax), netincomebeforetax),
    depreciation = COALESCE(VALUES(depreciation), depreciation),
    amortizationexpense = COALESCE(VALUES(amortizationexpense), amortizationexpense),
    interestexpense = COALESCE(VALUES(interestexpense), interestexpense),
    interestincome = COALESCE(VALUES(interestincome), interestincome),
    receivableincrease = COALESCE(VALUES(receivableincrease), receivableincrease),
    inventoryincrease = COALESCE(VALUES(inventoryincrease), inventoryincrease),
    accountspayable = COALESCE(VALUES(accountspayable), accountspayable),
    otherinvestingactivities = COALESCE(VALUES(otherinvestingactivities), otherinvestingactivities),
    othernoncurrentliabilitiesincrease = COALESCE(VALUES(othernoncurrentliabilitiesincrease), othernoncurrentliabilitiesincrease);
"""
insert_sql_financialstatement = f"""
INSERT INTO financialstatements (
    symbol, date, revenue, costsofgoodssold, grossprofit, 
    operatingexpenses, operatingincome, totalnonoperatingincomeandexpense, pretaxincome,
    incomefromcontinuingoperations, incomeaftertaxes, totalconsolidatedprofitfortheperiod, eps,
    equityattributabletoownersofparent, noncontrollinginterests, othercomprehensiveincome 
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
) ON DUPLICATE KEY UPDATE
    revenue = COALESCE(VALUES(revenue), revenue),
    costsofgoodssold = COALESCE(VALUES(costsofgoodssold), costsofgoodssold),
    grossprofit = COALESCE(VALUES(grossprofit), grossprofit),
    operatingexpenses = COALESCE(VALUES(operatingexpenses), operatingexpenses),
    operatingincome = COALESCE(VALUES(operatingincome), operatingincome),
    totalnonoperatingincomeandexpense = COALESCE(VALUES(totalnonoperatingincomeandexpense), totalnonoperatingincomeandexpense),
    pretaxincome = COALESCE(VALUES(pretaxincome), pretaxincome),
    incomefromcontinuingoperations = COALESCE(VALUES(incomefromcontinuingoperations), incomefromcontinuingoperations),
    incomeaftertaxes = COALESCE(VALUES(incomeaftertaxes), incomeaftertaxes),
    totalconsolidatedprofitfortheperiod = COALESCE(VALUES(totalconsolidatedprofitfortheperiod), totalconsolidatedprofitfortheperiod),
    eps = COALESCE(VALUES(eps), eps),
    equityattributabletoownersofparent = COALESCE(VALUES(equityattributabletoownersofparent), equityattributabletoownersofparent),
    noncontrollinginterests = COALESCE(VALUES(noncontrollinginterests), noncontrollinginterests),
    othercomprehensiveincome = COALESCE(VALUES(othercomprehensiveincome), othercomprehensiveincome);
"""
insert_sql_stockprice = f"""
INSERT INTO stockprices (
    symbol, date, trading_volume, trading_money, open, max, min, close, spread, trading_turnover
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
) ON DUPLICATE KEY UPDATE
    trading_volume = COALESCE(VALUES(trading_volume), trading_volume),
    trading_money = COALESCE(VALUES(trading_money), trading_money),
    open = COALESCE(VALUES(open), open),
    max = COALESCE(VALUES(max), max),
    min = COALESCE(VALUES(min), min),
    close = COALESCE(VALUES(close), close),
    spread = COALESCE(VALUES(spread), spread),
    trading_turnover = COALESCE(VALUES(trading_turnover), trading_turnover);
"""
# Method for running thread
def run_threaded(job_func, *args):
    job_thread = threading.Thread(target = job_func, args = args)
    job_thread.start()
# Method for removing outdated jobs
def remove_outdated_jobs(tz):
    # This function will remove the 'stocks' jobs after 1:30 PM Taipei time
    now = datetime.datetime.now(tz)
    if now.hour >= 13 and now.minute >= 30:
        schedule.clear('currentprice')
        print("Removed scheduled stock price thread...")
        logging.info("Removed scheduled current stock price thread")
# Method for scheduling the currentprice update
def schedule_currentprice_update(connection, tz, interval):
    now = datetime.datetime.now(tz)
    if 9 <= now.hour < 13 or (now.hour == 13 and now.minute < 30):
        run_threaded(update_currentprice, connection, interval)

# Method to update every table present within mySQL database
def update():
    connection = create_connection(host, user, password, database) # Establish SQL connection
     # Update through threading and scheduling
    currentprice_minutes = 5 # define interval for updating current price
    tz = pytz.timezone('Asia/Taipei')
    # schedule update_currentprice to run every {minutes} minutes 
    schedule.every(currentprice_minutes).minutes.do(schedule_currentprice_update, connection, tz, currentprice_minutes).tag('currentprice')
    # schedule news updates to run every 2 hours
    schedule.every(0.25).minutes.do(run_threaded, update_news, connection).tag('news')
    # schedule other updates for other market times
    pre_market_time = "07:30" # run once for pre market
    post_market_time = "14:00" # run second time post market
    # pre market run
    schedule.every().day.at(pre_market_time).do(run_threaded, update_stocks, connection)
    schedule.every().day.at(pre_market_time).do(run_threaded, update_financials, connection, "TaiwanStockBalanceSheet", columns_list_balancesheet, insert_sql_balancesheet)
    schedule.every().day.at(pre_market_time).do(run_threaded, update_financials, connection, "TaiwanStockCashFlowsStatement", columns_list_cashflow, insert_sql_cashflow)
    schedule.every().day.at(pre_market_time).do(run_threaded, update_financials, connection, "TaiwanStockFinancialStatements", columns_list_financialstatement, insert_sql_financialstatement)
    schedule.every().day.at(pre_market_time).do(run_threaded, update_dividends, connection)
    schedule.every().day.at(pre_market_time).do(run_threaded, update_index, connection)
    schedule.every().day.at(pre_market_time).do(run_threaded, update_financials, connection, "TaiwanStockPrice", columns_list_stockprice, insert_sql_stockprice)
    # post market run
    schedule.every().day.at(post_market_time).do(run_threaded, update_news, connection)
    schedule.every().day.at(post_market_time).do(run_threaded, update_stocks, connection)
    schedule.every().day.at(post_market_time).do(run_threaded, update_financials, connection, "TaiwanStockBalanceSheet", columns_list_balancesheet, insert_sql_balancesheet)
    schedule.every().day.at(post_market_time).do(run_threaded, update_financials, connection, "TaiwanStockCashFlowsStatement", columns_list_cashflow, insert_sql_cashflow)
    schedule.every().day.at(post_market_time).do(run_threaded, update_financials, connection, "TaiwanStockFinancialStatements", columns_list_financialstatement, insert_sql_financialstatement)
    schedule.every().day.at(post_market_time).do(run_threaded, update_dividends, connection)
    schedule.every().day.at(post_market_time).do(run_threaded, update_index, connection)
    schedule.every().day.at(post_market_time).do(run_threaded, update_financials, connection, "TaiwanStockPrice", columns_list_stockprice, insert_sql_stockprice)

    # Run the scheduler on loop until the end of the day (11:59 PM)
    end_of_day_time = datetime.time(23, 59, 0)
    end_of_day = datetime.datetime.combine(datetime.datetime.now(tz).date(), end_of_day_time, tz)

    print("Entering scheduler loop...")
    logging.info("Entering scheduler loop...")
    # Run the scheduler in a loop for the entire day
    while datetime.datetime.now(tz)< end_of_day:
        try:
            schedule.run_pending()
        except Exception as e:
            print(f"Error: {e}")
            logging.error(f"Error occurred during scheduler/threading method update(): {e}")
        remove_outdated_jobs(tz)
        time.sleep(60) # sleep for 60 seconds
# App route
@app.route('/update', methods = ['GET'])
def update_route():
    if request.headers.get('Handshake') == 'confirmed': # request for handshake (security)
        update() # call the update function
        return jsonify({'status':200, 'message':'Success'})
    else:
        return jsonify({'status':400, 'message':'Fail'})
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level = logging.INFO)
    logging.info("Deployment of service confirmed...")
    app.run(host = '0.0.0.0', port = int(os.environ.get('PORT', 8080)))
    # connection = create_connection(host, user, password, database) #Establish SQL connection
    # Code for creating tables
    # execute_query(connection, create_newstable)
    # execute_query(connection, create_stocktable)
    # execute_query(connection, create_balancesheettable)
    # execute_query(connection, create_cashflowtable)
    # execute_query(connection, create_financialstatements)
    # execute_query(connection, create_stockprices)
    # execute_query(connection, create_dividendrates)
    # execute_query(connection, create_marketindex)
    # execute_query(connection, create_currentpricetable)

    # Section to update all databases
    # update_news(connection)
    # update_stocks(connection)
    # update_financials(connection, "TaiwanStockBalanceSheet", columns_list_balancesheet, insert_sql_balancesheet)
    # update_financials(connection, "TaiwanStockCashFlowsStatement", columns_list_cashflow, insert_sql_cashflow)
    # update_financials(connection, "TaiwanStockFinancialStatements", columns_list_financialstatement, insert_sql_financialstatement)
    # update_dividends(connection)
    # update_index(connection)
    # update_financials(connection, "TaiwanStockPrice", columns_list_stockprice, insert_sql_stockprice)
    # update_currentprice(connection, 5)
    # update(connection) # update everything through scheduling and threading

    # Queries to SQL database
    # print(execute_read_query(connection, "newsarticles", "SELECT keywords FROM newsarticles;"))
    # print(execute_read_query(connection, "stocks", "SELECT shortname, businesssummary, longbusinesssummary FROM stocks;"))
