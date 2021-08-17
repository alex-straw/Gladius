import pandas as pd
import numpy as np


def prepare_spreadsheets(df):
    # (1) df: | unix | date | token | Token price USD | size | current holdings |

    """ REQUIRES TESTING: START """

    # Only buy orders will directly affect the cost basis
    # Only sell orders will directly lead to capital gains / losses

    df['previous holdings'] = df['current_holdings'].shift()
    df.at[0, 'previous holdings'] = 0

    df['sign'] = np.sign(df['size'])  # Identifies 'BUY' +1, and 'SELL' -1.

    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings |
    # | 2 | unix | date | LINK  |       10        |  +50 |        50        |         0         |
    # | 3 | unix | date | LINK  |       25        |  -25 |        25        |         50        |
    # | 4 | unix | date | LINK  |       20        |  +25 |        50        |         25        |

    # Create a column named 'cost_basis' and fill it with NaN
    df['cost_basis'] = np.NaN
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings |  cost_basis  |
    # | 2 | unix | date | LINK  |       10        |  +50 |        50        |         0         |      NaN     |
    # | 3 | unix | date | LINK  |       25        |  -25 |        25        |         50        |      NaN     |
    # | 4 | unix | date | LINK  |       20        |  +25 |        50        |         25        |      NaN     |

    buy_df = df[df['sign'] == 1].copy()
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings | cost_basis |
    # | 2 | unix | date | LINK  |       10        |  +50 |        50        |         0         |      0     |
    # | 4 | unix | date | LINK  |       20        |  +25 |        50        |         25        |      0     |

    sell_df = df[df['sign'] == -1].copy()
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings | cost_basis |
    # | 3 | unix | date | LINK  |       25        |  -25 |        25        |         50        |      0     |

    # Vectorised prior to loop to minimise processing done within for loop
    buy_df["price_x_size"] = (buy_df["Token price USD"] * buy_df["size"])
    buy_df.reset_index(drop=True, inplace=True)  # Reset index for for loop
    # Set up the first cost_basis --> equal to the very first purchase price
    buy_df.at[0, 'cost_basis'] = buy_df['Token price USD'].values[0]

    #  Time this section of code --> no straightforward vectorisation obvious
    for i in range(1, len(buy_df)):
        # cost basis = (Token price USD * trade size + previous cost basis USD * previous holdings) / current_holdings                   
        buy_df.loc[i, 'cost_basis'] = (buy_df.loc[i, 'price_x_size'] + (buy_df.loc[i, 'previous holdings'] * buy_df.loc[i - 1, 'cost_basis'])) / buy_df.loc[i, 'current_holdings']

    buy_df = buy_df.drop('price_x_size', 1)  # Drop temporary calculation column prior to merge

    merged_dataframe = pd.concat([buy_df, sell_df])
    merged_dataframe = merged_dataframe.sort_values(by=['date'])
    merged_dataframe["cost_basis"] = merged_dataframe["cost_basis"].ffill()  # Forward fill cost basis (sell orders)
    merged_dataframe.reset_index(drop=True, inplace=True)

    merged_dataframe['price_change'] = merged_dataframe["Token price USD"] - merged_dataframe["cost_basis"]

    return merged_dataframe


def get_profit_loss(df,name):
    sell_df = df[df['sign'] == -1].copy()

    sell_df['trade_status'] = np.sign(df['price_change'])

    loss_df = sell_df[sell_df['trade_status'] == -1].copy()
    profit_df = sell_df[sell_df['trade_status'] == 1].copy()

    loss_df['total'] = loss_df['price_change'] * loss_df['size']
    profit_df['total'] = profit_df['price_change'] * profit_df['size'] * -1

    crypto_cap_gains = profit_df['total'].sum()
    crypto_cap_losses = loss_df['total'].sum()

    loss_gain_data = np.array([name, crypto_cap_gains, crypto_cap_losses])

    return loss_gain_data


def calculate(cryptos_traded, df, file_paths):
    # Prepare data
    profit_loss_data = []

    for name in cryptos_traded:
        df[name] = prepare_spreadsheets(df[name])

        profit_loss_data.append(get_profit_loss(df[name], name))

    profit_loss_df = pd.DataFrame(data=profit_loss_data, columns=["name", "gains", "losses"])

    return df, profit_loss_df
