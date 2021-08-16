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

    # Next step is to re-merge the buy_df and sell_df
    # Resort by date
    # df['cost_basis'].fillna(method='ffill') --> this will set all sell cost basis values to first non zero cell above

    merged_dataframe = pd.concat([buy_df, sell_df])
    merged_dataframe = merged_dataframe.sort_values(by=['date'])

    merged_dataframe["cost_basis"] = merged_dataframe["cost_basis"].ffill()

    merged_dataframe.reset_index(drop=True, inplace=True)

    """ REQUIRES TESTING: END """

    return merged_dataframe


def calculate(cryptos_traded, df, file_paths):
    # Prepare data
    for name in cryptos_traded:
        df[name] = prepare_spreadsheets(df[name])

    return df
