# -*- coding: utf-8 -*-
"""
Created on Sunday August 09 12:34:00 2021
Author: Alex Straw
Description:
    Take Coinbase Pro fills data and output in the format:
    
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
    #df['secs'] = sub_minute_time

    return df


def organise_data(df):
    """ Standardises the Coinbase Pro fills document"""

    # FORMAT: | date | unix | side | c1 name | c1 size | c2 name | c2 size | c2 size USD |

    df = df.rename(columns={'created at': 'date',
                            'size unit': 'c1 name',
                            'size': 'c1 size',
                            'price/fee/total unit': 'c2 name',
                            'total': 'c2 size'
                            })

    df = add_unix_column(df)

    df['c1 size'] = df['c1 size'] * -1 * np.sign(df["c2 size"])  # Minus if SELL, plus if BUY

    df_required_cols = df[['date', 'unix', 'side', 'c1 name', 'c1 size', 'c2 name', 'c2 size']]

    return df_required_cols
