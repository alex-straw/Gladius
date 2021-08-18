import numpy as np
import pandas as pd


def group_same_day(unique_days, df):
    for day in unique_days:
        same_day_data = df.loc[(df['date'] == day)]


def get_days_traded(df):
    df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True).dt.normalize()
    df = df.set_index(pd.DatetimeIndex(df['date']))

    # Get unique days traded for building same day CGT portfolios
    unique_days = df['date'].unique()

    return unique_days, df


def group_transactions(crypto_dict):
    for name in crypto_dict:
        unique_days, df = get_days_traded(crypto_dict[name])

        group_same_day(unique_days, crypto_dict[name])

    return crypto_dict
