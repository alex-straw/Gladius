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
    
    # Strategy for optimising this calculation:
    
    # This strategy allows for the cost to be calculated without splitting dfs into BUY and SELL orders
    # This is because the 'cost_basis_size' will be lead to a 0 weighting in SELL cases, and correctly leave the cost basis 
    # unchanged to that of the most recent 'BUY' order above - simplifying the process.
    
    # | unix | date | token | Token price USD | size | current_holdings | previous_holdings | cost_basis_size | cur_trans_wt |
    # | unix | date | LINK  |       10        |  +50 |        50        |         0         |        50       |     500      |
    # | unix | date | LINK  |       10        |  -10 |        40        |         50        |        0        |     0        |
    
    # Step 1: Create an identical column
    df['cur_cost_basis_size'] = df['size']
    # Step 2: If the sign of a size column is negative (SELL), set the corresponding value in 'cost_basis_size' to 0 
    df.loc[np.sign(df['size']) == -1, 'cost_basis_size'] = 0
    
    # Step 3: cur_trans_wt - current transaction weighting
    # Step 3: prev_trans_wt - previous transaction weighting
    df['cur_trans_wt'] = df['Token price USD'] * df['cur_cost_basis_size']
             
    # Recursive process that uses previous cost basis to calculate following cost basis.
    # current_cost_basis = ((Token price USD * (size above 0)) + (previous_holdings*previous_cost_basis))/current_holdings 

                             
   """ REQUIRES TESTING: END """
    
    return df


def calculate(df, file_paths):
    # Prepare data
    for name in df:
        df[name] = prepare_spreadsheets(df[name])

    return df
