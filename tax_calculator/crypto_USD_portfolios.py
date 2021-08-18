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

    return c1s_traded, crypto_portfolios


def tidy_portfolio(df, crypto, file_paths):
    """
    This function builds a new data frame that only contains:
        -itself
        -USD

    This is done to prep for tax calculations later - as they are resolved in FIAT
    """

    columns_lhs = ['date', 'unix', 'c1 name', 'c1 size', 'c1 unit price USD']
    columns_rhs = ['date', 'unix', 'c2 name', 'c2 size', 'c2 unit price USD']

    #   This is necessary as some coins can act similarly to FIAT - as a medium of exchange (e.g BTC/ETH)
    #   They are present in both columns: c1, and c2.
    left_side_transactions = df[df['c1 name'] == crypto]
    left_side_df = pd.DataFrame(left_side_transactions, columns=columns_lhs)

    right_side_transactions = df[df['c2 name'] == crypto]
    right_side_df = pd.DataFrame(right_side_transactions, columns=columns_rhs)

    left_side_df = left_side_df.rename(columns={'unix': 'unix',
                                                'side': 'side',
                                                'c1 name': 'token',
                                                'c1 unit price USD': 'Token price USD',
                                                'c1 size': 'size'})

    right_side_df = right_side_df.rename(columns={'unix': 'unix',
                                                  'side': 'side',
                                                  'c2 name': 'token',
                                                  'c2 unit price USD': 'Token price USD',
                                                  'c2 size': 'size'})

    df = pd.concat([left_side_df, right_side_df])

    df = df.sort_values(by="date")
    df = df.reset_index(drop=True)

    df['current_holdings'] = df['size'].cumsum()
    df['value'] = df['size'] * df['Token price USD']
    df['sign'] = np.sign(df['size'])

    return df


def make_portfolios(df, file_paths):
    c1s_traded, crypto_portfolios = get_crypto_dataframes(df)
    crypto_portfolios['BTC'].to_csv(file_paths['results'] + "\Bitcoin.csv")

    for name in crypto_portfolios:
        crypto_portfolios[name] = tidy_portfolio(crypto_portfolios[name], name, file_paths)

        crypto_portfolios[name]['trade_type'] = np.where(crypto_portfolios[name]['sign'] == 1, 'acquisition', 'disposal')

    return c1s_traded, crypto_portfolios
