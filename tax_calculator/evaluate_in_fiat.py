import pandas as pd
import numpy as np


def get_data(specific_excel_file):
    """Read CSV data and store within a Pandas data frame"""
    file_path = os.getcwd() + specific_excel_file
    # temporarily set display precision
    df = pd.read_csv(file_path, skiprows=1)
    return df


def get_external_prices(df,data_path):
    """ Retrieves prices for a given unix time """
    token_prices = []
    price_data = pd.read_csv(data_path, skiprows=1)

    for time in df['unix']:
        row = df[df['unix'] == time]
        price = row.iloc[0]['open']
        token_prices.append(price)
    df['c2 unit price'] = token_prices


def get_c2_dataframes(df):
    """
    C2s - or currency 2s, are the resolving currencies for all transactions on Coinbase
    Typically these are [BTC,ETH,GBP,EUR,USD,USDC,USDT]...

    This function creates a dictionary of data frames for each c2.
    These are populated and priced separately.
    This is done to minimise required memory by having fewer large data frames open
    """
    c2_list = df["c2 name"].unique()
    c2_portfolio = {}

    for currency in c2_list:
        c2_portfolio[currency] = pd.DataFrame()
        c2_portfolio[currency] = c2_portfolio[currency].append([df[df['c2 name'] == currency]])


    return c2_list, c2_portfolio


def get_prices(df):
    c2_list, c2_portfolio = get_c2_dataframes(df)

    exchange_rates = {'USDC': 1,
                      'GBP': 1.38,
                      'EUR': 1.19,
                      'USD': 1,
                      'DAI': 1
                      }

    external_data = {'BTC': r"C:\Users\alexa\Desktop\price_data\Binance_BTCUSDT_minute.csv",
                     'ETH': r"C:\Users\alexa\Desktop\price_data\Binance_ETHUSDT_minute.csv"
                     }

    for c2 in c2_portfolio:
        print(c2)

    return df
