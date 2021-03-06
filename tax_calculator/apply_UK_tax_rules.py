# -*- coding: utf-8 -*-

"""
Created on Wed Sept 22 23:08:00 2021
Author: Alex Straw

Description:
    Takes the dictionary of crypto-fiat transactions

    Applies UK tax laws in the following order:
        1) Same day
        2) 30 day rule
        3) S104 pool

    Source: https://www.gov.uk/hmrc-internal-manuals/cryptoassets-manual/crypto22200

"""

import numpy as np
import pandas as pd
import datetime as datetime

"""--------------------------------30 DAY & S104 RULES--------------------------------"""


class S104Pool(object):
    """
    Each crypto asset has a S104 pool
    The S104 pool reflects assets that have been held for longer periods of time.
    """

    def __init__(self, name):
        self.name = name
        self.s104_quantity = 0
        self.s104_pool_value = 0

    def get_s104_pool_qty(self):
        return self.s104_quantity

    def get_s104_pool_value(self):
        return self.s104_pool_value

    def acquisition_s104(self, acq_value, quantity):
        """ Update s104 pool to reflect a new acquisition of crypto"""
        self.s104_pool_value += acq_value
        self.s104_quantity += quantity

    def disposal_s104(self, disp_value, s104_quantity_sold):
        """ Return gain when crypto is sold from the S104 pool"""
        if disp_value < 0.00000001:  # Handles boundary cases where value < e-10
            return 0
        else:
            s104_pool_value_reduction = (s104_quantity_sold / self.s104_quantity) * self.s104_pool_value

            if s104_quantity_sold == self.s104_quantity:
                gain = disp_value - self.get_s104_pool_value()
                self.s104_quantity = 0
                self.s104_pool_value = 0
                return gain
            else:
                gain = disp_value - s104_pool_value_reduction
                self.s104_quantity -= s104_quantity_sold
                self.s104_pool_value -= s104_pool_value_reduction
                return gain


def match_up(disp_size, acqs):
    """
    This function assigns disposals to acquisitions in a first-fit basis
    - As is specified by HMRC guidance on the 30 day rule
    """
    rem_acqs = np.copy(acqs)  # Duplicate acquisitions array for updating
    leftover_disp = disp_size

    for i in range(0, len(rem_acqs)):
        if leftover_disp >= rem_acqs[i]:
            leftover_disp = leftover_disp - rem_acqs[i]
            rem_acqs[i] = 0
        else:
            rem_acqs[i] -= leftover_disp
            leftover_disp = 0
    return rem_acqs, leftover_disp


def get_assigned_qtys(leftover_disp, disp_size, total_disp_value):
    """
    :param leftover_disp: total disposal quantity that could not be assigned to acquisitons (30 day rule)
    :param disp_size: Initial disposal quantity prior to matching
    :param total_disp_value: Total disposal value in fiat

    :return rem_s104_qty: Remaining crypto tokens that must be disposed from the s104 pool
    :return rem_s104_value: Remaining crypto value that must be disposed from the s104 pool
    :return rem_s104_value: Total value of disposed crypto that was matched to proceeding 30 day acquisitions
    """

    rem_s104_qty = leftover_disp
    rem_s104_value = (leftover_disp / disp_size) * total_disp_value
    thirty_day_disp_value = total_disp_value - rem_s104_value

    return rem_s104_qty, rem_s104_value, thirty_day_disp_value


def calculate_thirty_day_gain(start_acqs, rem_acqs, acqs_value, thirty_day_disp_value):
    """ This function calculates the fiat gain/loss from disposals which are reacquired in the proceeding 30 days"""

    quantity_per_acq = start_acqs - rem_acqs
    fraction_per_acq = quantity_per_acq / start_acqs

    less_allowable_costs = fraction_per_acq * acqs_value
    new_acqs_value_pool = acqs_value - less_allowable_costs

    less_allowable_costs_tot = sum(less_allowable_costs)

    gain = thirty_day_disp_value - less_allowable_costs_tot

    return gain, new_acqs_value_pool


def update_data_frame(df, rem_acqs, rem_acqs_value, indexes):
    for n in range(0, len(indexes)):
        df.loc[indexes[n], ['unmatched_acqs', 'residual_pool_value']] = rem_acqs[n], rem_acqs_value[n]
    return df


def get_thirty_day_acqs(df, start_date):
    """
    :return acqs: Acquisition quantities of the token in the 30 days proceeding a disposal
    :return acqs_value: Acquisition allowable costs --> indexes match 'acqs'
    """

    end_date = start_date + datetime.timedelta(days=30)  # 30 day cutoff date
    mask = (df['date'] >= start_date) \
           & (df['date'] <= end_date) \
           & (df['trade_type'] == 'acquisition') \
           & (df['unmatched_acqs'] > 0)  # Ignores acquisitions that are already fully matched to disposals

    relevant_df = df.loc[mask]  # Select only acquisitions between the start and end date

    acqs = np.array(relevant_df['unmatched_acqs'])
    acqs_value = np.array(relevant_df['residual_pool_value'])

    return acqs, acqs_value, relevant_df.index.values


def handle_disposal(df, index, s104_obj):
    """
    This function handles a single disposal, once conducted, the entire unmatched acquisitions is updated
    to prevent double reassignment.
    """

    cols_req_disp = ['date', 'quantity_token', 'residual_pool_value']
    start_date, disp_quantity, total_disp_value = df.loc[index][cols_req_disp]  # Current date

    acqs, acqs_value, row_indexes = get_thirty_day_acqs(df, start_date)

    if len(acqs) == 0:
        """ 
        Handles the case where there are no acquisitions in the next days.  It can be assumed that all of the gains
        for this disposal can be handled directly by interacting with the s104 pool. 
        """
        if abs(disp_quantity - s104_obj.s104_quantity) < 0.00001:
            # Where difference between disposal quantity and s104 quantity held is negligible, set them equal.
            disp_quantity = s104_obj.s104_quantity

        s104_gain = s104_obj.disposal_s104(total_disp_value, disp_quantity)
        df.loc[index, 'net_s104_pool'] = s104_gain  # Update spreadsheet with s104 gains
        rem_acqs = acqs
    else:
        """
        If there are acquisitions in the proceeding 30 days following a disposal, first match these using the 
        30 day rule.  Once all 30-day matching has taken place, match remaining disposals to those held in the 
        s104 pool.
        """
        rem_acqs, leftover_disp = match_up(disp_quantity, acqs)

        rem_s104_qty, rem_s104_value, thirty_day_disp_value = get_assigned_qtys(leftover_disp, disp_quantity,
                                                                                total_disp_value)

        # If disposals are matched to acquisitions --> acqs_value is overwritten to reflect new pooled value
        gain_thirty_day, acqs_value = calculate_thirty_day_gain(acqs, rem_acqs, acqs_value, thirty_day_disp_value)
        df.loc[index, 'net_thirty_day'] = gain_thirty_day  # Update spreadsheet with 30 day gains

        if abs(rem_s104_qty - s104_obj.s104_quantity) < 0.0000001:
            # Where difference between disposal quantity and s104 quantity held is negligible, set them equal.
            rem_s104_qty = s104_obj.s104_quantity

        if rem_s104_qty != 0:
            s104_gain = s104_obj.disposal_s104(rem_s104_value, rem_s104_qty)
            df.loc[index, 'net_s104_pool'] = s104_gain  # Update spreadsheet with s104 gains

    #  Final step is to update the table
    df = update_data_frame(df, rem_acqs, acqs_value, row_indexes)

    return df


def match_crypto(df, s104_obj):
    for i in range(0, len(df)):
        """ Loop through each day of trading in the data frame """

        if df.loc[i, 'trade_type'] == 'acquisition':
            """ Update s104 if an acquisition is reached with unmatched crypto """
            s104_obj.acquisition_s104(df.loc[i, 'residual_pool_value'], df.loc[i, 'unmatched_acqs'])

        if df.loc[i, 'trade_type'] == 'disposal':
            df = handle_disposal(df, i, s104_obj)

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
        s104_obj = S104Pool(name)  # Initialise a s104 pool for each crypto currency that is traded

        # Unmatched tokens will be gradually be matched and reduced.  Quantity token will remain unchanged.
        crypto_dict[name]['net_thirty_day'] = [0] * len(crypto_dict[name])
        crypto_dict[name]['net_s104_pool'] = [0] * len(crypto_dict[name])
        crypto_dict[name]['residual_pool_value'] = abs(crypto_dict[name]['residual_pool_value'])

        crypto_dict[name] = add_unmatched_acq_col(crypto_dict[name])

        crypto_dict[name] = match_crypto(crypto_dict[name], s104_obj)

    return crypto_dict


"""--------------------------------SAME DAY RULES--------------------------------"""


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

        if abs(residual) < 0.000001:
            # Handles edge cases --> YFI and Sushi each with 1e-12 remaining
            trade_type.extend(['resolved'])
            quantity_token.extend([0])
            residual_pool_value.extend([0])
            net_same_day.extend([pooled_value_disp - pooled_value_acq])
        else:
            if residual > 0:
                # if the residual is greater than 0 --> it is a net acquisition for the day
                trade_type.extend(['acquisition'])
                quantity_token.extend([residual])

                # Multiply cost basis of coins bought by the exact amount disposed
                # Subtract the full 'pooled disposal amount' for the day
                # This gives a net gain or loss according to the 'Same Day Rule' : TCGA1992/S105

                net_same_day.extend([(pooled_value_disp - (quantity_disposed / quantity_acquired) * pooled_value_acq)])

                # Calculate the value of the pooled assets remaining
                residual_pool_value.extend([(residual / quantity_acquired) * pooled_value_acq])

            if residual < 0:
                # if the residual is less than 0 --> it is a net disposal for the day
                trade_type.extend(['disposal'])
                quantity_token.extend([residual * -1])  # Note minus sign

                # Calculate the remaining pooled allowable costs for the disposal
                residual_pool_value.extend([(residual / quantity_disposed) * pooled_value_disp])

                # This gives a net gain or loss according to the 'Same Day Rule' : TCGA1992/S105

                net_same_day.extend([(quantity_acquired / quantity_disposed) * pooled_value_disp - pooled_value_acq])

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


def master_func(crypto_dict):
    """
    Calls each rule sequentially according to HMRC rules (22/09/2021)
    """

    def apply_same_day_rule(df):
        unique_days, df = get_days_traded(df)
        df = group_same_day(unique_days, df)
        return df

    def apply_thirty_day_s104_pool(df, name):
        s104_obj = S104Pool(name)  # Initialise a s104 pool for each crypto currency that is traded

        # Unmatched tokens will be gradually be matched and reduced.  Quantity token will remain unchanged.
        df['net_thirty_day'] = [0] * len(df)
        df['net_s104_pool'] = [0] * len(df)
        df['residual_pool_value'] = abs(df['residual_pool_value'])

        df = add_unmatched_acq_col(df)
        df = match_crypto(df, s104_obj)
        return df

    for name in crypto_dict:
        crypto_dict[name] = apply_same_day_rule(crypto_dict[name])
        crypto_dict[name] = apply_thirty_day_s104_pool(crypto_dict[name], name)

    return crypto_dict
