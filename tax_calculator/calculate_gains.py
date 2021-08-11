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
   
    # Step 1: Create an identical column
    df['cost_basis_size'] = df['size']
    # Step 2: If the sign of a size column is negative (SELL), set the corresponding value in 'cost_basis_size' to 0 
    df.loc[np.sign(df['size']) == -1, 'cost_basis_size'] = 0
                           
    # Important to note that on this spreadsheet the 'previous_holdings' column may refer to sell orders that are not present.
    # This is key as it allows for correct cost basis weightings.
                           
    # Recursive process that uses previous cost basis to calculate following cost basis.
    # current_cost_basis = ((Token price USD * abs(size)) + (previous_holdings*previous_cost_basis))/current_holdings 
    
                           
                           
    
    sell_df = sell_df.append(np.sign([df[df['size']) == -1]])
                             
   """ REQUIRES TESTING: END """
    
    return df


def calculate(df, file_paths):
    # Prepare data
    for name in df:
        df[name] = prepare_spreadsheets(df[name])

    return df
