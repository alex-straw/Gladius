# -*- coding: utf-8 -*-
"""
Created on Sunday August 09 12:34:00 2021
Author: Alex Straw
Description:
    Take Coinbase fills data and output in the format:

    | dd/mm/yyyy | unix | side | c1 name | c1 size | c2 name | c2 size | c2 size USD |
"""

import pandas as pd
import numpy as np
import os
import re


def add_unix_column(df):
    """
    Conversion from CBPRO Time to useable Rounded Unix format
    Returns:
        Unix time accurate to the nearest 60 second
        Position in the minute for price interpolation
    -----------------------------------------------------
                        Initial State:
    '2021-02-28T17:14:30.966Z'
    -----------------------------------------------------
    -----------------------------------------------------
                        Second Form:
    date = '13/02/2020' exact_time = '16:25:29'
    -----------------------------------------------------
    -----------------------------------------------------
                        Third form:
    date_unix = '1.61e12...' time_unix '46013.123'
    -----------------------------------------------------
    -----------------------------------------------------
                        Final form:
    df['unix'] = array of unix timestamps e.g 1.61e12
    -----------------------------------------------------
    """

    complete_unix_time = []
    sub_minute_time = []

    exact_time_pattern = "T(.*)."
    day_pattern = "(.*)T"

    for time in df['date']:
        initial_time = re.search(exact_time_pattern, time).group(1)  # Select data after letter 'T'
        time_split = np.array(initial_time.split(':', -1))
        time_split_float = time_split.astype(float)

        power_array_time = [3600, 60, 1]
        seconds_elapsed_day = sum(time_split_float * power_array_time)
        rounded_seconds_day = int(60 * round(float(seconds_elapsed_day) / 60)) * 1000  # Unix has 1/1000th s accuracy
        second_position = seconds_elapsed_day % 60

        initial_date = re.search(day_pattern, time).group(1)  # Select data before letter 'T'
        initial_date = initial_date.split('-', -1)  # Split date by hyphen
        date = str(initial_date[0]) + "/" + str(initial_date[1]) + "/" + str(initial_date[2])  # Standard format

        unix_date = (pd.to_datetime([date]).astype(np.int64) / 10 ** 6)

        time_test = (unix_date[0] + rounded_seconds_day)
        complete_unix_time.append(time_test)

        sub_minute_time.append(second_position)

    df['unix'] = np.float64(complete_unix_time)
    # df['secs'] = sub_minute_time

    return df


def get_home_currency(df):
    """Used to find the home currency given by the cb spreadsheet - should be GBP"""
    cb_cols = [col for col in df.columns if 'Subtotal' in col]
    home_currency = cb_cols[0].split(" ", 1)[0]
    return home_currency


def organise_data(df):
    """
        Standardises the Coinbase fills document
        NEED TO SET SIGN TO PLUS OR MINUS DEPENDING ON TRANSACTION TYPE
        otherwise no consistency with how calculation for the coinbase pro document is done
        """

    standard_transaction = {
        'Buy': 'BUY',
        'Receive': 'BUY',
        'Coinbase Earn': 'BUY',
        'Sell': 'SELL',
        'Send': 'SELL',
        'Convert': 'IGNORE'
    }

    # Standardise columns for implementation with coinbase pro fills data
    df = df.rename(columns={'Timestamp': 'date',
                            'Transaction Type': 'side',
                            'Asset': 'c1 name',
                            'Quantity Transacted': 'c1 size',
                            'GBP Spot Price at Transaction': 'c1 unit price'
                            })

    df = add_unix_column(df)

    home_currency = get_home_currency(df)

    # Standardise the Coinbase sides - buy/sell/send/receive/coinbase_earn etc

    standard_sides = []
    for transaction in df['side']:
        standard_sides.append(standard_transaction[transaction])

    df['side'] = standard_sides

    # Get rid of all transactions that are send - receive - etc (keeps Coinbase Earn).
    df = df[df['side'] != 'IGNORE']

    # Creates equivalent price/fee/total unit depending on row names --> same as CBpro document - could be EUR or USD
    df['c2 name'] = [home_currency] * len(df)

    df['bool_series'] = pd.isnull(df["GBP Total (inclusive of fees)"])
    df.loc[df['bool_series'] == True, 'GBP Total (inclusive of fees)'] = df['c1 unit price'] * df['c1 size']

    df['c2 size'] = df['GBP Total (inclusive of fees)']

    # This sets the 'size' column for each token depending on the transaction type - BUY / SELL
    # A negative sign represents that currency being used as payment
    # A positive sign represents that currency being received

    df['side_sign'] = df['side'].apply(lambda x: 1 if x == 'BUY' else -1)
    df['c2 size'] = df['c2 size'] * df['side_sign'] * - 1
    df['c1 size'] = df['c1 size'] * df['side_sign']

    # Rename corresponding to CB_PRO dataframe
    df_required_cols = df[['date', 'unix', 'side', 'c1 name', 'c1 size', 'c2 name', 'c2 size']]

    return df_required_cols
