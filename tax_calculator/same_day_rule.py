import numpy as np
import pandas as pd

def group_same_day(unique_days,df):
    pass


def get_days_traded(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index(pd.DatetimeIndex(df['date']))

    # Get unique days traded for building same day CGT portfolios
    unique_days = df["date"].dt.normalize().unique()

    return unique_days, df


def group_transactions(crypto_dict):

    for name in crypto_dict:
        unique_days, df = get_days_traded(crypto_dict[name])

        group_same_day(unique_days,crypto_dict[name])


    return crypto_dict