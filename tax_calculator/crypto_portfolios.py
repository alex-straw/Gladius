import pandas as pd
import numpy as np


def get_crypto_dataframes(df):
    """ make a portfolio for each unique cryptocurrency traded in c1 column """
    c1s_traded = df['c1 name'].unique()
    crypto_portfolios = {}

    for c1 in c1s_traded:
        crypto_portfolios[c1] = pd.DataFrame()

    for crypto in crypto_portfolios:
        # Add transactions whose 'size unit' is the same as the crypto, to its respective data frame
        crypto_portfolios[crypto] = crypto_portfolios[crypto].append([df[df['c1 name'] == crypto]])

        # Add transactions whose 'price/fee/total unit' is the same as the crypto, to its respective data frame
        crypto_portfolios[crypto] = crypto_portfolios[crypto].append([df[df['c2 name'] == crypto]])

        crypto_portfolios[crypto] = crypto_portfolios[crypto].sort_values(by="unix")
        crypto_portfolios[crypto] = crypto_portfolios[crypto].reset_index(drop=True)

    return crypto_portfolios


def make(df):
    crypto_portfolios = get_crypto_dataframes(df)

    for name in crypto_portfolios:
        print(name)

    return crypto_portfolios




