import pandas as pd
import numpy as np


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
            pass
    print(s104_pool_allowable_costs)

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
        crypto_dict[name]['unmatched_tokens'] = crypto_dict[name]['quantity_token']
        crypto_dict[name]['residual_pool_value'] = abs(crypto_dict[name]['residual_pool_value'])

        crypto_dict[name] = match_crypto(crypto_dict[name])

    return crypto_dict
