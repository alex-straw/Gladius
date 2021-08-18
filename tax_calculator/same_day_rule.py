import numpy as np
import pandas as pd


def same_day_pool(df, trade_type):
    df_trade_type = df.loc[(df['trade_type'] == trade_type)]
    quantity = df_trade_type['size'].sum()
    pooled_value = df_trade_type['value'].sum()

    return quantity, pooled_value


def group_same_day(unique_days, df):
    trade_type = []
    quantity_token = []
    residual_pool_value = []
    net_same_day = []

    for day in unique_days:
        same_day_data = df.loc[(df['date'] == day)]

        quantity_acquired, pooled_value_acq = same_day_pool(same_day_data, trade_type='acquisition')
        quantity_disposed, pooled_value_disp = same_day_pool(same_day_data, trade_type='disposal')

        quantity_disposed = quantity_disposed * -1  # Set disposal values to be positive sign for consistency with HMRC
        pooled_value_disp = pooled_value_disp * -1

        # Next stage is to assess if the day is a net disposal, acquisition, or resolved: (BUY=SELL)
        # Same day transactions will all be handled prior to pass of main algorithm
        # Planned data frame output --> each unique day will have a single transaction
        # | date | token_quantity | pooled_value | trade type | net same day |

        residual = quantity_acquired - quantity_disposed

        if residual > 0:
            # if the residual is greater than 0 (net acquisition for the day):
            trade_type.extend(['acquisition'])
            quantity_token.extend([residual])

            # Multiply cost basis of coins bought by the exact amount disposed
            # Subtract the full 'pooled disposal amount' for the day
            # This gives a net gain or loss according to the 'Same Day Rule' : TCGA1992/S105

            net_same_day.extend([(quantity_disposed / quantity_acquired) * pooled_value_acq - pooled_value_disp])

            # Calculate the value of the pooled assets remaining
            residual_pool_value.extend([(residual / quantity_acquired) * pooled_value_acq])

        if residual < 0:
            # if the residual is less than 0 (net disposal for the day):
            trade_type.extend(['disposal'])
            quantity_token.extend([residual * -1])  # Note minus sign

            # Calculate the remaining pooled allowable costs for the disposal
            residual_pool_value.extend([(residual / quantity_disposed) * pooled_value_disp])

            # This gives a net gain or loss according to the 'Same Day Rule' : TCGA1992/S105

            net_same_day.extend([pooled_value_acq - (quantity_acquired / quantity_disposed) * pooled_value_disp])

        if residual == 0:
            trade_type.extend(['resolved'])
            quantity_token.extend([0])
            residual_pool_value.extend([0])
            net_same_day.extend([pooled_value_acq - pooled_value_disp])

    same_day_df = {'date': unique_days,
                   'trade_type': trade_type,
                   'quantity_token': quantity_token,
                   'residual_pool_value': residual_pool_value,
                   'net_same_day': net_same_day
                   }

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
