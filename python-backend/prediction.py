from data import execute_query, execute_read_query
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import matplotlib.pyplot as plt # Version 3.8.0
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler # Version 1.4.0
import pandas as pd # Version 2.1.4
import numpy as np # Version 1.26.0
from decimal import Decimal
import torch # Version 2.2.0
import torch.nn as nn # Same as above

# Load environmental variables from .env file within python-backend
load_dotenv()
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")
instance = os.getenv("INSTANCE_CONNECTION_NAME")

# Method for connecting to mySQL database
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name, # COMMENT (for local)
            # unix_socket = f"/cloudsql/{instance}", # UNCOMMENT (for gcloud)
            user = user_name,
            passwd = user_password,
            database = db_name
        )
        print("Connection to MySQL DB successful!")
        # logging.info('Connection to MySQL DB successful!')
    except Error as e:
        print(f"Error {e} during connection to database")
        # logging.error(f"Error {e} occurred during connection to MySQL database")
    return connection
# Checking for null values within a dataframe (throws exception if NULL detected)
def check_null(df):
    # Identify rows with any null values
    null_rows = df[df.isnull().any(axis=1)]
    # Check if null_rows is not empty
    if not null_rows.empty:
        # Return the DataFrame containing only rows with null values
        # print(null_rows) # COMMENT THIS
        iloc_indexes = [df.index.get_loc(label) for label in null_rows.index]
        return null_rows
    else:
      print("No null values were found within the dataframe!")
      return pd.DataFrame()
# Function that imputes based on median (looks forward and backward within column)
def imputation(df, null_rows):
    print("Entering standard imputation process...")
    for index, row in null_rows.iterrows():
        for col in df.columns:
            if pd.isna(df.at[index, col]):
                # Gather up to 3 previous and 4 next non-NaN values
                values_before = df[col].iloc[max(0, index-3):index].dropna()
                values_after = df[col].iloc[index+1:min(df.shape[0], index+5)].dropna()
                if len(values_before) < 3:
                    # Not enough previous, take next 7 valid after current, if available
                    additional_values_after = df[col].iloc[min(df.shape[0], index+5):min(df.shape[0], index+8)].dropna()
                    values_after = pd.concat([values_after, additional_values_after]).head(7)
                elif len(values_after) < 4:
                    # Not enough after, take previous 7 valid before current, if available
                    additional_values_before = df[col].iloc[max(0, index-7):index-3].dropna()
                    values_before = pd.concat([additional_values_before, values_before]).tail(7)
                # Combine and find median
                combined_values = pd.concat([values_before, values_after]).median()
                # Impute value
                df.at[index, col] = combined_values
    print("Imputation completed!")
    return df
# Combining dataframes based on full date range
def reindex(df, full_date_range):
    base_df = pd.DataFrame(full_date_range, columns=['Date'])
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure 'Date' is datetime for merging
    # check_not_null(df)
    df_merged = pd.merge(base_df, df, on='Date', how='left')
    return df_merged

# Checking for null values within a dataframe (throws exception if NULL detected)
def check_not_null(df):
    not_null_rows = df.dropna(how='any')  # This drops rows where any value is NaN
    if not not_null_rows.empty:
        print("Rows without null values:")
        print(not_null_rows)
        return not_null_rows
    else:
        print("All rows contain at least one null value within the dataframe!")
        return pd.DataFrame()  # Return an empty DataFrame for consistency
# News imputation method (filling in all NaN values with 0.500 sentiment)
def impute_news(df):
  print("Entering news imputation process...")
  df['sentiment'] = df['sentiment'].apply(lambda x: float(x) if isinstance(x, Decimal) else x) # convert all sentiment values to float
  for i in range(len(df)):
        # Skip if the current row's sentiment is not null
        if not pd.isnull(df.iloc[i]['sentiment']):
            continue
        # Find indices of previous and next non-null sentiments within 14 days
        prev_index = next_index = None
        for j in range(i - 1, max(-1, i - 8), -1):
            if not pd.isnull(df.iloc[j]['sentiment']) and (df.iloc[i]['Date'] - df.iloc[j]['Date']).days <= 14:
                prev_index = j
                break
        for j in range(i + 1, min(len(df), i + 8)):
            if not pd.isnull(df.iloc[j]['sentiment']) and (df.iloc[j]['Date'] - df.iloc[i]['Date']).days <= 14:
                next_index = j
                break
        # Calculate mean sentiment if both previous and next non-null sentiments are found
        if prev_index is not None and next_index is not None:
            mean_sentiment = df.iloc[prev_index:next_index + 1]['sentiment'].mean()
        elif prev_index is not None:  # Only previous non-null sentiments are available
            mean_sentiment = df.iloc[max(0, prev_index - 6):prev_index + 1]['sentiment'].mean()
        elif next_index is not None:  # Only next non-null sentiments are available
            mean_sentiment = df.iloc[next_index:min(len(df), next_index + 7)]['sentiment'].mean()
        else:  # No non-null sentiments are found within 14 days
            mean_sentiment = 0.500  # Default value
        # Impute the calculated mean sentiment
        df.at[df.index[i], 'sentiment'] = mean_sentiment
  print("News imputation process completed!")
  return df
# Function for advanced imputation
def imputation_adjusted(df, null_rows):
  print("Entering imputation with backfill process...")
  for index, row in null_rows.iterrows():
      for col in df.columns:
          if pd.isna(df.at[index, col]):
              # Gather up to 3 previous and 4 next non-NaN values
              values_before = df[col].iloc[max(0, index-3):index].dropna()
              values_after = df[col].iloc[index+1:min(df.shape[0], index+5)].dropna()
              if len(values_before) < 3:
                  additional_values_after = df[col].iloc[index+1:min(df.shape[0], index+8)].dropna()
                  values_after = pd.concat([values_after, additional_values_after]).head(7)
              if len(values_after) < 4:
                  additional_values_before = df[col].iloc[max(0, index-7):index].dropna()
                  values_before = pd.concat([additional_values_before, values_before]).tail(7)
              # If still not enough values, use backfill
              if len(values_before) + len(values_after) < 4:
                  # Find the next available non-null value to use for backfill
                  for next_valid_index in range(index + 1, df.shape[0]):
                      if not pd.isna(df.at[next_valid_index, col]):
                          backfill_value = df.at[next_valid_index, col]
                          break
                  else:  # If no non-null value is found in the future, backfill_value remains as NaN
                      backfill_value = np.nan
                  # Apply backfill value
                  df.at[index, col] = backfill_value
              else:
                  # If sufficient values are found, calculate the median for imputation
                  combined_values = pd.concat([values_before, values_after]).median()
                  df.at[index, col] = combined_values
  print("Backfill imputation completed!")
  return df
#Function for simple backfill and forward fill imputation
def impute_financials(df):
  print("Entering impute financials process...")
  # Fill columns that are entirely NULL with zeros
  for col in df.columns:
      if df[col].isnull().all():
          df[col].fillna(0, inplace=True)
  # Backfill and forward fill for each column based on the earliest and latest non-null entries
  for col in df.columns:
      # Find the first non-null value and backfill
      first_non_null = df[col].first_valid_index()
      if first_non_null is not None:
          df[col].loc[:first_non_null] = df[col].loc[first_non_null]

      # Find the last non-null value and forward fill
      last_non_null = df[col].last_valid_index()
      if last_non_null is not None:
          df[col].loc[last_non_null:] = df[col].loc[last_non_null]
  # Fill in-between values based on the previous available entry
  df.ffill(inplace = True) # df.fillna(method='ffill', inplace=True)
  print("Impute financials process completed!")
  return df
# Function for filling a dataframe up based on the first non-NaN value found within each individual column
def impute_fill(df):
  for column in df.columns:
    first_non_null = df[column].first_valid_index()
    if first_non_null is not None:
    #   print(f"NOT NULL {first_non_null}")
      first_non_null_value = df.at[first_non_null, column]
      df[column] = df[column].fillna(first_non_null_value)
  return df
# Data processing function
def data_processing(target, full_date_range, financial = True):
    # Imputing and cleaning up market index
    df = pd.DataFrame(target)
    df['Date'] = pd.to_datetime(df['date']).dt.date
    df.set_index('Date', inplace=True)
    df.drop('date', axis = 1, inplace = True)
    df.sort_values(by = 'Date', inplace = True)
    df.reset_index(inplace = True)
    df.drop('symbol', axis = 1, inplace = True)
    if financial:
        df_reindexed = reindex(df, full_date_range)
    else:
        sector = df.iloc[0]['sector']
        industry = df.iloc[0]['industry']
        base_df = pd.DataFrame(full_date_range, columns=['Date'])
        base_df['Date'] = pd.to_datetime(base_df['Date'])
        df['Date'] = pd.to_datetime(df['Date'])
        df_reindexed = pd.merge(base_df, df, on='Date', how='left')
        df_reindexed['sector'] = df_reindexed['sector'].fillna(sector)
        df_reindexed['industry'] = df_reindexed['industry'].fillna(industry)
        df_reindexed['Date'] = pd.to_datetime(df_reindexed['Date'])
        df_imputed = df_reindexed
    # Check for null values and perform imputation
    null_index = check_null(df_reindexed)
    if not null_index.empty:
        if financial:
            df_imputed = impute_financials(df_reindexed)
        else:
            df_imputed = impute_fill(df_reindexed)
    null_output = check_null(df_imputed) # final check to make sure no null values
    if not null_output.empty:
        check_not_null(df_imputed)
        print(df_imputed)
        raise Exception("Something went wrong, null values were still found even after imputation")
    # print(df_imputed[df_imputed['Date'] <= '1997-07-02'])
    return df_imputed

# Function to normalize features
def normalize_features(df, feature_columns):
    scaler = MinMaxScaler()
    df[feature_columns] = scaler.fit_transform(df[feature_columns])
    return df, scaler

class StockPredictor(nn.Module):  # Assuming this is your LSTM model class
    def __init__(self, input_dim, hidden_dim, num_layers, prediction_window):
        super(StockPredictor, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        # self.prediction_window = prediction_window
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, prediction_window)

    def forward(self, x):
        # Initialize hidden state with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device = x.device).requires_grad_()
        # Initialize cell state
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim, device = x.device).requires_grad_()
        # print("X_batch_tensor shape:", x.shape)
        # print("h0 shape:", h0.shape)
        # print("c0 shape:", c0.shape)

        # Detach the hidden state to prevent exploding/vanishing gradients
        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))
        # print("Shape after LSTM:", out.shape)
        # Apply fully connected layer to last time step
        out = self.fc(out[:, -1, :])
        # Reshape the output to have dimensions [batch_size, prediction_window]
        out = out.view(x.size(0), -1)  # Reshaping to ensure the output matches the prediction_window
        # print("Shape after taking hidden state out of last time step:", out.shape)
        return out


# Main Below
if __name__ == "__main__":
    pd.options.mode.chained_assignment = None  # Suppress specific SettingWithCopyWarning
    try:
        connection = create_connection(host, user, password, database) # Establish SQL connection
        symbols = execute_read_query(connection, 'stocks', "SELECT symbol, shortname FROM stocks;")
        symbol_dict = {entry['symbol']:entry['shortname'] for entry in symbols} # {'2330':'台積電', '2392':'...}
        interest = '2330' # Stock symbol of interest
        basic_info_dict = execute_read_query(connection, 'stocks', f"SELECT shortname, longname FROM stocks WHERE symbol = '{interest}';")
        shortname = basic_info_dict[0].get('shortname')
        longname = basic_info_dict[0].get('longname')
        historical_prices = execute_read_query(connection, 'stockprices', f"SELECT * FROM stockprices WHERE symbol = '{interest}';")

        twse_index = execute_read_query(connection, 'marketindex', f"SELECT * FROM marketindex WHERE index_symbol = '^TWII';")
        balance = execute_read_query(connection, 'balancesheets', f"SELECT * FROM balancesheets WHERE symbol = '{interest}';")
        cash = execute_read_query(connection, 'cashflow', f"SELECT * FROM cashflow WHERE symbol = '{interest}';")
        financial = execute_read_query(connection, 'financialstatements', f"SELECT * FROM financialstatements WHERE symbol = '{interest}';")
        stock = execute_read_query(connection, 'stocks', f"SELECT symbol, date, sector, industry FROM stocks WHERE symbol = '{interest}';")
        news = execute_read_query(connection, 'newsarticles', "SELECT pubdate, keywords, sentiment FROM newsarticles;")
        tsmc_news = [entry for entry in news for key, value in entry.items() if key == 'keywords' and value != None and (shortname in value or longname in value)]
        # print(stock)
        # convert to dataframe
    except Error as e:
        raise Exception("Error occurrence during fetch data phase:\n" + str(e))
    else:
        if connection:
            connection.close()
            print("Connection closed upon successful retrieval of data")
    # Block for standard imputation (historical stock prices)
    print("Entering historical price data section for", interest)
    # Imputing for historical stock price
    historical_df = pd.DataFrame(historical_prices)
    # Convert 'date' to date object within pandas and set as index
    historical_df['Date'] = pd.to_datetime(historical_df['date']).dt.date
    historical_df.set_index('Date', inplace=True)
    # Drop the original 'date' and 'symbol' columns
    historical_df.drop(['date', 'symbol'], axis=1, inplace=True)
    # Create a complete date range
    start_date = historical_df.index.min()
    end_date = historical_df.index.max()
    full_date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    # Reindex the DataFrame to this full date range
    historical_df_reindexed = historical_df.reindex(full_date_range)
    # # Impute missing values using median
    # imputer = SimpleImputer(strategy='median')
    # # print(f"Columns: {historical_df_reindexed.columns}")
    # # print(f"Index: {historical_df_reindexed.index}")
    # historical_df_imputed = pd.DataFrame(imputer.fit_transform(historical_df_reindexed), columns=historical_df_reindexed.columns, index=historical_df_reindexed.index)
    historical_df = historical_df_reindexed
    # Reset index
    historical_df.reset_index(inplace=True)
    historical_df.rename(columns={'index': 'Date'}, inplace=True)

    # Check for gaps
    # date_diff = historical_df_imputed['Date'].diff()
    # gaps = historical_df_imputed[date_diff > pd.Timedelta(days=1)]
    null_rows = check_null(historical_df)
    if not null_rows.empty:
        historical_df_imputed = imputation(historical_df, null_rows)
        null_output = check_null(historical_df_imputed) # final check to make sure no null values

    # Imputing News sentiment Section
    print("Entering news process for", interest)
    if len(tsmc_news) == 0:
        print("News relevant to company of interest not found, initializing empty dataframe")
        news_df = pd.DataFrame()
        news_df['Date'] = []
        news_df['sentiment'] = []
    else:
        try:
            news_df = pd.DataFrame(tsmc_news)
            news_df['Date'] = pd.to_datetime(news_df['pubdate']).dt.date # Convert to only just date
        except KeyError as ke:
            print("Encountered key error:", ke)
        else:
            news_df.set_index('Date', inplace = True) # set date column as index
            news_df.drop('pubdate', axis = 1, inplace = True) # drop "pubdate" column
            news_df.drop('keywords', axis = 1, inplace = True) # drop "keywords" column as well
            news_df.reset_index(inplace = True)
            news_df.rename(columns = {'index':'Date'}, inplace = True)
        # Sort the DataFrame by the 'Date' column
        news_df.sort_values(by='Date', inplace=True)
        news_df.reset_index(inplace = True)
        news_df.drop('index', axis = 1, inplace = True)
    news_df_reindexed = reindex(news_df, full_date_range)
    news_df_imputed = impute_news(news_df_reindexed)
    null_news = check_null(news_df_imputed) # Ensure that there are no null values
    if not null_news.empty:
        raise Exception("Something went wrong with the imputation news process")
    # Imputing and cleaning up market index
    print("Cleaning up market index data for", interest)
    twse_df = pd.DataFrame(twse_index)
    twse_df['Date'] = pd.to_datetime(twse_df['date']).dt.date
    twse_df.set_index('Date', inplace=True)
    twse_df.drop(['date', 'volume'], axis = 1, inplace = True)
    twse_df.sort_values(by = 'Date', inplace = True)
    twse_df.reset_index(inplace = True)
    # twse_df.drop('index', axis = 1, inplace = True)
    twse_df.drop('index_symbol', axis = 1, inplace = True)
    twse_df_reindexed = reindex(twse_df, full_date_range)
    # Check for null values and perform imputation
    null_index = check_null(twse_df_reindexed)
    if not null_index.empty:
        twse_df_imputed = imputation_adjusted(twse_df_reindexed, null_index)
        null_output = check_null(twse_df_imputed) # final check to make sure no null values

    # Imputing and processing balancesheet, cashflow and financials
    print("Imputation for balance sheet for company", interest)
    balance_df = data_processing(balance, full_date_range)
    print("Imputation for cash flow for company", interest)
    cash_df = data_processing(cash, full_date_range)
    print("Imputation for financial statements for company", interest)
    financial_df = data_processing(financial, full_date_range)
    print("For categorical variables in table 'stocks':")
    # For the sector and industry (categorical variables)
    stock_df = data_processing(stock, full_date_range, False)

    # Combine the dataframes into one big dataframe based on the column ('Date)
    print("Entering merge section for master dataframe, company", interest)
    merge1 = pd.merge(historical_df_imputed, news_df_imputed, on = 'Date', how = 'left')
    merge2 = pd.merge(merge1, twse_df_imputed, on = 'Date', how = 'left')
    merge3 = pd.merge(merge2, balance_df, on = 'Date', how = 'left')
    merge4 = pd.merge(merge3, cash_df, on = 'Date', how = 'left')
    merge5 = pd.merge(merge4, financial_df, on = 'Date', how = 'left')
    merged_df = pd.merge(merge5, stock_df, on = 'Date', how = 'left')
    #rename certain columns
    merged_df = merged_df.rename(columns = {'open_x':'open', 'close_x':'close'})
    merged_df = merged_df.rename(columns = {'open_y':'market_open', 'close_y':'market_close', 'high':'market_high', 'low':'market_low', 'adj_close':'market_adj_close'})
    null = check_null(merged_df)
    if not null.empty:
        print(null)
        raise Exception ("Something went wrong, null values should not be present within merged df")
    # print(merged_df.shape)
    # print(merged_df.columns)
    # print(merged_df.head())

    # AI Deep Learning through LSTM
    # Assuming 'merged_df' is your DataFrame and 'open' is the target column
    merged_df = pd.get_dummies(merged_df, columns=['sector', 'industry']) # one-hot encode sector and industry
    merged_df.drop('Date', axis = 1, inplace = True) # drop the 'Date ' column
    # Adjust these values based on your dataset
    input_dim = len(merged_df.columns)
    hidden_dim = 50  # Example value
    num_layers = 2  # Example value

    total_rows = len(merged_df)
    short_start, long_start = -365-30, -1460 # One year & Three years
    short_pred = -30 # 30 days back
    long_pred = -365 # 365 days back
    short_test = merged_df.iloc[short_start:short_pred] # A year + 30 days back
    long_test = merged_df.iloc[long_start:long_pred] # Three years + 365 days back
    # Normalize features first
    # Select columns to normalize, excluding 'Date' and the target column 'open'
    feature_columns = [col for col in short_test.columns if col != 'open']
    # Normalize features (excluding 'open')
    short_df, _ = normalize_features(short_test, feature_columns)
    long_df, _ = normalize_features(long_test, feature_columns)
    # Normalize target ('open')
    target_scaler = MinMaxScaler()
    short_df['open'] = target_scaler.fit_transform(short_df[['open']])
    long_df['open'] = target_scaler.fit_transform(long_df[['open']])

    # Commence Prediction
    short_seq_length = 365
    short_prediction_window = 30
    epochs = 10
    short_term = 'short_term_model.pth'
    # Short term Model
    short_model = StockPredictor(input_dim, hidden_dim, num_layers, short_prediction_window)
    if short_term in os.listdir():
        if torch.cuda.is_available():
            short_model.load_state_dict(torch.load(short_term))
        else:
            short_model.load_state_dict(torch.load(short_term, map_location=torch.device('cpu')))
        short_model.eval()
    else:
        print(os.listdir())
        raise Exception("No short term model state dict found")
    short_data_np = short_df.values  # This converts the DataFrame to a 2D NumPy array
    short_data = torch.tensor([short_data_np], dtype = torch.float32)
    # short_data = short_data.unsqueeze(0)
    # Predict
    with torch.no_grad():
        short_predictions = short_model(short_data)
    # Inverse normalization
    short_prediction = target_scaler.inverse_transform(short_predictions).tolist()[0] # convert to list data type
    short_actual = merged_df['open'].iloc[short_start:].values.tolist() # convert to list data type
    # print(merged_df['open'].iloc[short_pred:])

    # For long term model
    long_seq_length = 365*3 # 3 years (anything more than that can lead to not having enough validation data)
    long_prediction_window = 365
    long_term = 'long_term_model.pth'
    # Long term Model
    long_model = StockPredictor(input_dim, hidden_dim, num_layers, long_prediction_window)
    if long_term in os.listdir():
        if torch.cuda.is_available():
            long_model.load_state_dict(torch.load(long_term))
        else:
            long_model.load_state_dict(torch.load(long_term, map_location=torch.device('cpu')))
        long_model.eval()
    else:
        print(os.listdir())
        raise Exception("No long term model state dict found")
    long_data_np = long_df.values # This converts DataFrame to 2D NumPy Array (for prediction)
    long_data = torch.tensor([long_data_np], dtype = torch.float32)
    # Predict
    with torch.no_grad():
        long_predictions = long_model(long_data)
    # Inverse normalization
    long_prediction = target_scaler.inverse_transform(long_predictions).tolist()[0] # convert to list data type
    long_actual = merged_df['open'].iloc[long_start:].values.tolist() # convert to list data type

    # Graph them
    print(f"Full date range length: {len(full_date_range)}")
    # Set font properties for Chinese characters
    font = FontProperties(fname=r'SimSun.ttf', size=12)  # Adjust the path to your font file
    plt.rcParams['font.family'] = font.get_name()
    actual_short_dates = full_date_range[short_start:]
    actual_long_dates = full_date_range[long_start:]
    if not len(short_prediction) == (0-len(short_actual)) + (len(short_actual)-short_pred):
        print()
        print(f"short_prediction length: {len(short_prediction)}")
        print(f"short_actual: {len(short_actual)}")
        raise Exception("Length inconsistencies found between actual data and predictions for short term model")
    short_dates = full_date_range[short_pred:] # going back certain number of days
    # Plotting the first line plot (Short Prediction)
    plt.figure(figsize=(10, 5))  # Creating a figure
    plt.subplot(2, 1, 1)  # Creating the first subplot
    plt.plot(actual_short_dates, short_actual, label=f"{shortname} 實際股價", color = 'blue')  # Plotting the first line
    plt.plot(short_dates, short_prediction, label = f"AI 預測股價", color = 'red')
    plt.xlabel('日期', fontproperties = font)
    plt.ylabel('股價', fontproperties = font)
    plt.title(f"{longname} AI 短期股價趨勢預測比對", fontproperties = font)
    plt.legend(prop = font)
    plt.ylim(min(min(short_actual), min(short_prediction)) - 1, max(max(short_actual), max(short_prediction)) + 1) # Specifying a dynamic range for the y-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    if not len(long_prediction) == (0-len(long_actual)) + (len(long_actual)-long_pred):
        print()
        print(f"long_prediction length: {len(long_prediction)}")
        print(f"long_actual: {len(long_actual)}")
        raise Exception("Length inconsistencies found between actual data and predictions for long term model")
    long_dates = full_date_range[long_pred:]
    # Plotting the second line plot
    plt.subplot(2, 1, 2)  # Creating the second subplot
    plt.plot(actual_long_dates, long_actual, label=f"{shortname} 實際股價", color = 'blue')  # Plotting the second line
    plt.plot(long_dates, long_prediction, label = f"AI 預測股價", color = 'red')
    plt.xlabel('日期')
    plt.ylabel('股價')
    plt.title(f"{longname} AI 長期股價趨勢預測比對")
    plt.legend()
    plt.ylim(min(min(long_actual), min(long_prediction)) - 1, max(max(long_actual), max(long_prediction)) + 1) # Specifying a dynamic range for the y-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # Adjusting layout to prevent overlap
    plt.tight_layout()
    # Displaying the plots
    plt.show()