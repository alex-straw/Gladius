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
            s104_quantity_token += df.loc[i, 'unmatched_tokens']

        if df.loc[i, 'trade_type'] == 'disposal':
            time = df.loc[i, 'date']  # Current date
            end_date = time + datetime.timedelta(days=30)  # 30 day cutoff date

            disposal_quantity = df.loc[i, 'quantity_token']
            disposal_consideration = df.loc[i, 'residual_pool_value']
            allowable_cost_pool = 0
            print("--------------")
            print(disposal_quantity)

            # Look for acquisitions in the 30 days following a disposal to match crypto
            mask = (df['date'] > time) & (df['date'] <= end_date) & (df['trade_type'] == 'acquisition')
            acq_list = df.index[mask].tolist()

            for index in acq_list:
                original_quantity, unmatched_quantity, allowable_value = df.iloc[index][['quantity_token',
                                                                                         'unmatched_tokens',
                                                                                         'residual_pool_value']]
                # gain = consideration - less allowable costs

                if disposal_quantity > unmatched_quantity:
                    disposal_quantity -= unmatched_quantity
                    unmatched_quantity = 0
                    allowable_cost_pool += allowable_value

                if disposal_quantity < unmatched_quantity:
                    disposal_quantity = 0
                    unmatched_quantity -= disposal_quantity
                    allowable_cost_pool += (disposal_quantity/original_quantity)*allowable_value

                if disposal_quantity == unmatched_quantity:
                    disposal_quantity = 0
                    unmatched_quantity = 0
                    allowable_cost_pool += allowable_value

                df.at[index, 'unmatched_tokens'] = unmatched_quantity
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
        crypto_dict[name]['unmatched_tokens'] = crypto_dict[name]['quantity_token']
        crypto_dict[name]['residual_pool_value'] = abs(crypto_dict[name]['residual_pool_value'])

        crypto_dict[name] = match_crypto(crypto_dict[name])

    return crypto_dict
