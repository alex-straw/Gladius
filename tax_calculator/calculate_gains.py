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
    
    df['prev_cost_basis'] = 0  # Set up empty cost basis columns
    df['cur_cost_basis'] = 0
    
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings | prev_cost_basis | cur_cost_basis |
    # | 2 | unix | date | LINK  |       10        |  +50 |        50        |         0         |        0        |        0       |
    # | 3 | unix | date | LINK  |       25        |  -25 |        25        |         50        |        0        |        0       |
    # | 4 | unix | date | LINK  |       20        |  +25 |        50        |         25        |        0        |        0       |
    
    buy_df = buy_df.append([np.sign(df[df['size']) == 1]])
                            
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings | prev_cost_basis | cur_cost_basis |
    # | 2 | unix | date | LINK  |       10        |  +50 |        50        |         0         |        0        |        0       |
    # | 4 | unix | date | LINK  |       20        |  +25 |        50        |         25        |        0        |        0       |                       
                                         
                            
    sell_df = sell_df.append([np.sign(df[df['size']) == -1]])
                              
    # | x | unix | date | token | Token price USD | size | current_holdings | previous_holdings | prev_cost_basis | cur_cost_basis |
    # | 3 | unix | date | LINK  |       25        |  -25 |        25        |         50        |        0        |        0       |
                            
                             
   """ REQUIRES TESTING: END """
    
    return df


def calculate(df, file_paths):
    # Prepare data
    for name in df:
        df[name] = prepare_spreadsheets(df[name])

    return df
