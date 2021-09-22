import pandas as pd
import numpy as np


def get_crypto_dataframes(df):
    """
    --- get_crypto_dataframes() ---
    This function takes the complete data frame with GBP priced transactions.
    It creates a dictionary of data frames containing every transaction that involved that crypto-asset.
    For instance, Bitcoin is often bought with GBP, but also used to purchase other crypto currencies.
    Whatever the transaction, if Bitcoin is involved, that entire transaction is placed into this new
    crypto-specific portfolio.
    """

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
    --- tidy_portfolio() ---
    The vast complexity with crypto taxes is a result of crypto-crypto trading.  To simplify this, trades are simplified
    as shown below from a -> b(i),b(ii), splitting crypto-crypto trades into 2 separate trades resolved in fiat.
        a)      10 Eth --> 0.5 Bitcoin
        b) i)   10 Eth --> £10,000
        b) ii)  £10,000 --> 0.5 BTC
    """

    columns_lhs = ['date', 'unix', 'c1 name', 'c1 size', 'c1 unit price']
    columns_rhs = ['date', 'unix', 'c2 name', 'c2 size', 'c2 unit price']

    #   This is necessary as some coins can act similarly to FIAT - as a medium of exchange (e.g BTC/ETH)
    #   They are present in both columns: c1, and c2.
    left_side_transactions = df[df['c1 name'] == crypto]
    left_side_df = pd.DataFrame(left_side_transactions, columns=columns_lhs)

    right_side_transactions = df[df['c2 name'] == crypto]
    right_side_df = pd.DataFrame(right_side_transactions, columns=columns_rhs)

    left_side_df = left_side_df.rename(columns={'unix': 'unix',
                                                'side': 'side',
                                                'c1 name': 'token',
                                                'c1 unit price': 'Token price',
                                                'c1 size': 'size'})

    right_side_df = right_side_df.rename(columns={'unix': 'unix',
                                                  'side': 'side',
                                                  'c2 name': 'token',
                                                  'c2 unit price': 'Token price',
                                                  'c2 size': 'size'})

    df = pd.concat([left_side_df, right_side_df])

    df = df.sort_values(by="date")
    df = df.reset_index(drop=True)

    df['current_holdings'] = df['size'].cumsum()
    df['value'] = df['size'] * df['Token price']
    df['sign'] = np.sign(df['size'])

    return df


def make_portfolios(df, file_paths):
    """ takes complete GBP-priced, and chronologically sorted data frame output by 'get_standard_currency.py'
        returns a dictionary of data frames.  Each data frame contains only one crypto asset priced in GBP
    """

    c1s_traded, crypto_portfolios = get_crypto_dataframes(df)

    for name in crypto_portfolios:
        crypto_portfolios[name] = tidy_portfolio(crypto_portfolios[name], name, file_paths)

        crypto_portfolios[name]['trade_type'] = np.where(crypto_portfolios[name]['sign'] == 1, 'acquisition', 'disposal')

    return c1s_traded, crypto_portfolios
