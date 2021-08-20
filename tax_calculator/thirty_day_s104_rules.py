import pandas as pd
import numpy as np
import datetime as datetime


class S104Pool(object):
    """ This class is used to interract with each coins S104 pool """

    def __init__(self, name):
        self.name = name
        self.s104_quantity = 0
        self.s104_pool_value = 0

    def get_s104_quantity(self):
        return self.s104_quantity

    def get_s104_pool_value(self):
        return self.s104_pool_value

    def acquisition_s104(self, acq_value, quantity):
        """ Update s104 pool to reflect a new acquisition of crypto"""
        self.s104_quantity += quantity
        self.s104_pool_value += acq_value

    def disposal_s104(self, disp_value, s104_quantity_sold):
        """ Return gain when crypto is sold from the S104 pool"""

        if disp_value < 0.0000001:  # Handles boundary cases where value < e-10
            pass
        else:
            gain = disp_value - self.s104_pool_value * (s104_quantity_sold / self.s104_quantity)
            self.s104_quantity -= s104_quantity_sold
            return gain


def first_fill(disp_quantity, df):
    indexes = df.index.tolist()
    for index in indexes:
        acq_quantity, acq_value, acq_unmatched = df.loc[index, ['quantity_token',
                                                                'residual_pool_value',
                                                                'unmatched_acqs']]

        print(acq_quantity, acq_value, acq_unmatched)


def handle_disposal(df, index, s104_obj):
    cols_req_disp = ['date', 'quantity_token', 'residual_pool_value']
    date, disp_quantity, disp_value = df.loc[index][cols_req_disp]  # Current date
    end_date = date + datetime.timedelta(days=30)  # 30 day cutoff date

    mask = (df['date'] > date) & (df['date'] <= end_date) & (df['trade_type'] == 'acquisition')

    df_acq = df.loc[mask]

    if len(df_acq) == 0:
        """ Handles the case where there are no acquisitions in the next 30 days """
        s104_gain = s104_obj.disposal_s104(disp_value, disp_quantity)
        df.loc[index, 'net_s104_pool'] = s104_gain
    else:
        first_fill(disp_quantity, df_acq)

    return 20


def match_crypto(df, s104_obj):
    for i in range(0, len(df)):
        """ Loop through each day of trading in the data frame """

        if df.loc[i, 'trade_type'] == 'acquisition':
            """ Update s104 if an acquisition is reached with unmatched crypto """
            s104_obj.acquisition_s104(df.loc[i, 'residual_pool_value'], df.loc[i, 'unmatched_acqs'])

        if df.loc[i, 'trade_type'] == 'disposal':
            """ 
            If trade is a disposal:
                1. 30 day rule
                2. S104 pool
            """
            gain = handle_disposal(df, i, s104_obj)

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
        s104_obj = name + "_s104"
        s104_obj = S104Pool(name)  # Initialise a s104 pool for each crypto currency that is traded

        # Unmatched tokens will be gradually be matched and reduced.  Quantity token will remain unchanged.
        crypto_dict[name]['net_30_day'] = [0] * len(crypto_dict[name])
        crypto_dict[name]['net_s104_pool'] = [0] * len(crypto_dict[name])
        crypto_dict[name]['residual_pool_value'] = abs(crypto_dict[name]['residual_pool_value'])

        crypto_dict[name] = add_unmatched_acq_col(crypto_dict[name])

        crypto_dict[name] = match_crypto(crypto_dict[name], s104_obj)

    return crypto_dict
