import pandas as pd
import numpy as np
import datetime as datetime


def match_crypto(df):

    s104_pool_allowable_costs = 0
    s104_quantity_token = 0

    for i in range(1, len(df)):
        if df.loc[i, 'trade_type'] == 'acquisition':
            # As orders are handled chronologically, if any acquisition has unmatched shares when
            # it is reached, these can go directly into the s104 pool
            s104_pool_allowable_costs += df.loc[i, 'residual_pool_value']
            s104_quantity_token += df.loc[i, 'unmatched_acqs']

        if df.loc[i, 'trade_type'] == 'disposal':
            time = df.loc[i, 'date']  # Current date
            end_date = time + datetime.timedelta(days=30)  # 30 day cutoff date

            # 'Less allowable costs' for acquisitions that were assigned to disposals in the proceeding 30 day period
            allowable_cost_pool = 0

            disposal_quantity = df.loc[i, 'quantity_token']
            temp_disposal_quantity = disposal_quantity
            disposal_consideration = df.loc[i, 'residual_pool_value']

            # Look for acquisitions in the 30 days following a disposal to match crypto
            mask = (df['date'] > time) & (df['date'] <= end_date) & (df['trade_type'] == 'acquisition')
            acq_list = df.index[mask].tolist()

            """
            for index in acq_list:
                quantity_token, unmatched_quantity, allowable_value = df.iloc[index][['quantity_token',
                                                                                      'unmatched_tokens',
                                                                                      'residual_pool_value']]
            """

    return df


def add_unmatched_acq_col(df):
    df['unmatched_acqs'] = df['quantity_token']
    df.loc[(df['trade_type'] == 'disposal'), 'unmatched_acqs'] = 0
    return df


def final_pass(crypto_dict):
    """
    This function will act as the starting point for the 30 day, and S104 pool rules.
    Each row must be iterated over chronologically, and crypto matched from the first
    disposals to the first acquisitions in the proceeding 30 days.

    Each crypto asset will be handled separately prior to final capital gains summary.
    """

    for name in crypto_dict:
        # Unmatched tokens will be gradually be matched and reduced.  Quantity token will remain unchanged.
        crypto_dict[name]['net_30_day'] = [0] * len(crypto_dict[name])
        crypto_dict[name]['net_s104_pool'] = [0] * len(crypto_dict[name])
        crypto_dict[name]['residual_pool_value'] = abs(crypto_dict[name]['residual_pool_value'])

        crypto_dict[name] = add_unmatched_acq_col(crypto_dict[name])

        crypto_dict[name] = match_crypto(crypto_dict[name])

    return crypto_dict
