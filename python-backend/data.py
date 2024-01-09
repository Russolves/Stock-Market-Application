# Import all the necessary modules
import json
import os
import requests # Version: 2.31.0
from dotenv import load_dotenv # Version: 1.0.0
import mysql.connector # Version: 8.2.0
from mysql.connector import Error
import datetime
from snownlp import SnowNLP # Version: 0.12.3

# Load environmental variables from .env file within python-backend
load_dotenv()
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

# String for creating table
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
createstocktable = """
CREATE TABLE IF NOT EXISTS stocks (
    symbol VARCHAR()
)
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
    except Error as e:
        print(f"Error {e} during connection to database")
    return connection

# Method for executing SQL queries
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query execution successful!")
    except Error as e:
        print(f"The error {e} occurred")

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
        print(f"The error '{e}' occurred")

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
    nextpage = ''
    news_database = execute_read_query(connection, "newsarticles")
    article_id_ls = [value for entry in news_database for key, value in entry.items() if key == 'article_id']
    article_id_set = set(article_id_ls) # generate set of article_ids (database)
    # Check the news API 20 iterations each time
    for i in range(20):
        status, news, nextpage = retrieve_news(nextpage)
        if status['status'] == 'error': # exit if error occurs
            print(f"News API call error:\nMessage:{status['message']}\nCode:{status['code']}")
            break
        news_id_ls = [value for entry in news for key, value in entry.items() if key == 'article_id']
        news_id_set = set(news_id_ls) # generate set of article_ids (api call)
        new_news = list(news_id_set - article_id_set)
        news_data = [entry for entry in news for key, value in entry.items() if key == 'article_id' and value in new_news]
        for entry in news_data:
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
                    else:
                        keywords = value
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


if __name__ == "__main__":
    connection = create_connection(host, user, password, database) #Establish SQL connection
    # execute_query(connection, create_newstable)
    update_news(connection)
    # print(execute_read_query(connection, "newsarticles"))
