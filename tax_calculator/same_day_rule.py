import numpy as np
import pandas as pd


def same_day_pool(df, trade_type):
    df_trade_type = df.loc[(df['trade_type'] == trade_type)]
    token_amount = df_trade_type['size'].sum()
    value = df_trade_type['value'].sum()

    return token_amount, value


def group_same_day(unique_days, df):
    date = []
    tok_grouped_by_day = []
    value_grouped_by_day = []

    for day in unique_days:
        same_day_data = df.loc[(df['date'] == day)]

        token_acquired, value_acquired = same_day_pool(same_day_data, trade_type='acquisition')
        tok_grouped_by_day.extend([token_acquired])
        value_grouped_by_day.extend([value_acquired])
        date.extend([day])

        token_disposed, value_disposed = same_day_pool(same_day_data, trade_type='disposal')
        tok_grouped_by_day.extend([token_disposed])
        value_grouped_by_day.extend([value_disposed])
        date.extend([day])  # Important to duplicate the day to split into acquired and disposed separately

    trade_type = ['acquisition', 'disposal'] * len(unique_days)

    same_day_df = {'date': date,
                   'trade_type': trade_type,
                   'tokens': tok_grouped_by_day,
                   'value': value_grouped_by_day}
    df = pd.DataFrame(data=same_day_df)

    return df


def get_days_traded(df):
    df['date'] = pd.to_datetime(df['date'], infer_datetime_format=True).dt.normalize()
    df = df.set_index(pd.DatetimeIndex(df['date']))

    # Get unique days traded for building same day CGT portfolios
    unique_days = df['date'].unique()

    return unique_days, df


def group_transactions(crypto_dict):
    for name in crypto_dict:
        unique_days, df = get_days_traded(crypto_dict[name])

        crypto_dict[name] = group_same_day(unique_days, crypto_dict[name])

    return crypto_dict
