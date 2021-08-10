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
        row = price_data[price_data['unix'] == time]
        price = row.iloc[0]['open']
        token_prices.append(price)
    df['c2 unit price USD'] = token_prices


def get_c2_dataframes(df):
    """
    C2s - or currency 2s, are the resolving currencies for all transactions on Coinbase
    Typically these are [BTC,ETH,GBP,EUR,USD,USDC,USDT]...

    This function creates a dictionary of data frames for each c2.
    These are populated and priced separately.
    This is done to minimise required memory by having fewer large data frames open
    """
    c2_list = df["c2 name"].unique()
    c2_portfolios = {}

    for currency in c2_list:
        c2_portfolios[currency] = pd.DataFrame()
        c2_portfolios[currency] = c2_portfolios[currency].append([df[df['c2 name'] == currency]])

    return c2_list, c2_portfolios


def get_prices(df,file_paths):
    c2_list, c2_portfolios = get_c2_dataframes(df)

    exchange_rates = {'USDC': 1,
                      'GBP': 1.38,
                      'EUR': 1.19,
                      'USD': 1,
                      'DAI': 1
                      }

    for c2 in c2_portfolios:
        if c2 == 'BTC' or c2 == 'ETH':
            get_external_prices(c2_portfolios[c2], file_paths[c2])
        else:
            specific_rate = exchange_rates[c2]
            token_prices = [specific_rate] * len(c2_portfolios[c2])
            c2_portfolios[c2]['c2 unit price USD'] = token_prices

    df = pd.concat(c2_portfolios)
    df['c2 size USD'] = df['c2 unit price USD'] * df['c2 size']

    return df