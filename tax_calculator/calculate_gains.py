import pandas as pd
import numpy as np


def prepare_spreadsheets(df):
    df['previous holdings'] = df['current_holdings'].shift()
    df.at[0,'previous holdings'] = 0

    # df['cost basis'] = df['size'].apply(lambda x: 1 if x == 'BUY' else -1)
    return df


def calculate(df, file_paths):
    # Prepare data
    for name in df:
        df[name] = prepare_spreadsheets(df[name])

    return df
