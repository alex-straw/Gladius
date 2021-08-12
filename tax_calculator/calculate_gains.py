import pandas as pd
import numpy as np


def prepare_spreadsheets(df):
    
    # (1) df: | unix | date | token | Token price USD | size | current holdings |
        
    """ REQUIRES TESTING: START """
    
    # Only buy orders will directly affect the cost basis
    # Only sell orders will directly lead to capital gains / losses
    
    df['previous holdings'] = df['current_holdings'].shift()
    df.at[0,'previous holdings'] = 0
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings |
    # | 2 | unix | date | LINK  |       10        |  +50 |        50        |         0         |
    # | 3 | unix | date | LINK  |       25        |  -25 |        25        |         50        |
    # | 4 | unix | date | LINK  |       20        |  +25 |        50        |         25        |
    
    df['cost_basis'] = 0    # Set up empty cost basis column
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings | cost_basis |
    # | 2 | unix | date | LINK  |       10        |  +50 |        50        |         0         |      0     |
    # | 3 | unix | date | LINK  |       25        |  -25 |        25        |         50        |      0     |
    # | 4 | unix | date | LINK  |       20        |  +25 |        50        |         25        |      0     |
    
    buy_df = buy_df.append([np.sign(df[df['size']) == 1]])  
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings | cost_basis |
    # | 2 | unix | date | LINK  |       10        |  +50 |        50        |         0         |      0     |
    # | 4 | unix | date | LINK  |       20        |  +25 |        50        |         25        |      0     |
                            
    
    # Vectorised prior to loop to minimise processing done within for loop                 
    buy_df['price_x_size'] = buy_df['Token price USD'] * buy_df['size']

    # Time this section of code --> no straightforward vectorisation obvious
    for i in range(1, len(buy_df)):
        # cost basis = (Token price USD * trade size + previous cost basis USD * previous holdings) / current_holdings                   
        buy_df.loc[i, 'cost_basis'] = (df.loc[i, 'price_x_size'] + df.loc[i, 'previous_holdings'] * df.loc[i-1, 'cost_basis'])/df.loc[i, 'current_holdings']


    sell_df = sell_df.append([np.sign(df[df['size']) == -1]])
                              
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings | cost_basis |
    # | 3 | unix | date | LINK  |       25        |  -25 |        25        |         50        |      0     |
                            
                             
   """ REQUIRES TESTING: END """
    
    return df


def calculate(df, file_paths):
    # Prepare data
    for name in df:
        df[name] = prepare_spreadsheets(df[name])

    return df
