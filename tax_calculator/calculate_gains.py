import pandas as pd
import numpy as np


def prepare_spreadsheets(df):
    
    # (1) df: | unix | date | token | Token price USD | size | current holdings |
    
    df['previous holdings'] = df['current_holdings'].shift()
    df.at[0,'previous holdings'] = 0
    
     # (2) df: | unix | date | token | Token price USD | size | current_holdings | previous_holdings |
        
    """ REQUIRES TESTING: START """
    
    # Test these lines
    
    # Only buy orders will directly affect the cost basis
    # Only sell orders will directly lead to capital gains / losses
    
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings |
    # | 2 | unix | date | LINK  |       10        |  +50 |        50        |         0         |
    # | 3 | unix | date | LINK  |       25        |  -25 |        25        |         50        |
    # | 4 | unix | date | LINK  |       20        |  +25 |        50        |         25        |
    
    buy_df = buy_df.append([np.sign(df[df['size']) == 1]])
                            
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings |
    # | 2 | unix | date | LINK  |       10        |  +50 |        50        |         0         |
    # | 4 | unix | date | LINK  |       20        |  +25 |        50        |         25        |
                            
    sell_df = sell_df.append([np.sign(df[df['size']) == -1]])
                              
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings |
    # | 3 | unix | date | LINK  |       25        |  -25 |        25        |         50        |
                            
                             
   """ REQUIRES TESTING: END """
    
    return df


def calculate(df, file_paths):
    # Prepare data
    for name in df:
        df[name] = prepare_spreadsheets(df[name])

    return df
