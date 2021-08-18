import numpy as np
import pandas as pd


def same_day_pool(df, trade_type):
    df_trade_type = df.loc[(df['trade_type'] == trade_type)]
    quantity = df_trade_type['size'].sum()
    pooled_value = df_trade_type['value'].sum()

    return quantity, pooled_value


def group_same_day(unique_days, df):

    for day in unique_days:
        same_day_data = df.loc[(df['date'] == day)]

        quantity_acquired, pooled_value_acq = same_day_pool(same_day_data, trade_type='acquisition')

        quantity_disposed, pooled_value_disp = same_day_pool(same_day_data, trade_type='disposal')
        quantity_disposed = quantity_disposed * -1  # Set values to be positive sign for consistency with HMRC
        pooled_value_disp = pooled_value_disp * -1

        residual = quantity_acquired - quantity_disposed

        # Next stage is to assess if the day is a net disposal, acquisition, or resolved: (BUY=SELL)
        # Same day transactions will all be handled prior to pass of main algorithm
        # Planned data frame output --> each unique day will have a single transaction
        # | date | token_quantity | pooled_value | trade type | net same day |

        print(residual)


        """
    date = []
    tok_grouped_by_day = []
    value_grouped_by_day = []
        tok_grouped_by_day.extend([token_acquired])
        value_grouped_by_day.extend([value_acquired])
        date.extend([day])

        tok_grouped_by_day.extend([token_disposed])
        value_grouped_by_day.extend([value_disposed])
        date.extend([day])  # Important to duplicate the day to split into acquired and disposed separately

    trade_type = ['acquisition', 'disposal'] * len(unique_days)

    same_day_df = {'date': date,
                   'trade_type': trade_type,
                   'token_quantity': tok_grouped_by_day,
                   'value_usd': value_grouped_by_day,
                   }

    df = pd.DataFrame(data=same_day_df)
    """

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
