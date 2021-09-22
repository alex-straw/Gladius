import pandas as pd
import numpy as np
import time


def get_data(specific_excel_file):
    """Read CSV data and store within a Pandas data frame"""
    file_path = os.getcwd() + specific_excel_file
    # temporarily set display precision
    df = pd.read_csv(file_path, skiprows=1)
    return df


def get_external_prices_efficient(df, data_path):
    """ Method for pricing BTC / ETH with respect to trade time """

    token_prices = []

    price_data = pd.read_csv(data_path, skiprows=1)

    unix_times = df['unix'].to_numpy()

    relevant_price_data = price_data.query('unix in @unix_times')

    for time in df['unix']:
        row = relevant_price_data[relevant_price_data['unix'] == time]
        price = row.iloc[0]['open']
        token_prices.append(price)

    df['c2 unit price USD'] = token_prices


def dict_dataframes(df, type):
    """
    C2s - or currency 2s, are the resolving currencies for all transactions on Coinbase
    Typically these are [BTC,ETH,GBP,EUR,USD,USDC,USDT]...

    This function creates a dictionary of data frames for each c2.
    These are populated and priced separately.
    This is done to minimise required memory by having fewer large data frames open
    """
    c_list = df[type].unique()
    c_portfolios = {}

    for currency in c_list:
        c_portfolios[currency] = pd.DataFrame()
        c_portfolios[currency] = df.loc[(df[type] == currency)].copy()

    return c_list, c_portfolios


def get_prices(df, file_paths):
    c2_list, c2_portfolios = dict_dataframes(df, "c2 name")

    exchange_rates = {'USDC': 1,
                      'GBP': 1.38,
                      'EUR': 1.19,
                      'USD': 1,
                      'DAI': 1
                      }

    for c2 in c2_portfolios:
        if c2 == 'BTC' or c2 == 'ETH':
            get_external_prices_efficient(c2_portfolios[c2], file_paths[c2])
        else:
            specific_rate = exchange_rates[c2]
            token_prices = [specific_rate] * len(c2_portfolios[c2])
            c2_portfolios[c2]['c2 unit price USD'] = token_prices

    df = pd.concat(c2_portfolios)

    # Convert from USD to GBP
    df['c2 unit price'] = df['c2 unit price USD'] / exchange_rates['GBP']

    df['c2 size fiat'] = df['c2 unit price'] * df['c2 size']
    df['c1 size fiat'] = df['c2 size fiat'] * - 1
    df['c1 unit price'] = abs(df['c2 size fiat'] / df['c1 size'])

    return df
