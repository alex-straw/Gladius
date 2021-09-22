# -*- coding: utf-8 -*-
"""
Created on Sunday Sept 13 15:10:00 2021
Author: Alex Straw

Description:
    Makes sure that the user's input is of the correct format prior to calculation
    and returns the user's data as a dictionary of one or more data frames.

    Current checks:
        1. Is the file a csv?
        2. Given an exchange, are the column names and their respective positions correct?
"""

import pandas as pd
import numpy as np
import os
import re
import sys


class RowError(Exception):
    pass


def get_correct_dfs_dict():
    """ Creates correct exchange formats for comparison against user input """

    correct_coinbase_format = {'Timestamp': ['2018-12-08T17:01:30Z'],
                               'Transaction Type': ['BUY'],
                               'Asset': ['BTC'],
                               'Quantity Transacted': [2],
                               'GBP Spot Price at Transaction': [4000],
                               'GBP Subtotal': [8000],
                               'GBP Total (inclusive of fees)': [8050],
                               'GBP Fees': [50],
                               'Notes': ['string_string_string']}
    correct_coinbase_df = pd.DataFrame(correct_coinbase_format)

    correct_coinbase_pro_format = {'portfolio' : ['default'],
                                   'trade id': [501],
                                   'product': ['SUSHI-BTC'],
                                   'side': ['BUY'],
                                   'created at': ['2018-12-08T17:01:30Z'],
                                   'size': [0.5],
                                   'size unit': ['SUSHI'],
                                   'price': [0.0003193],
                                   'fee': [0.000000265019],
                                   'total': [-0.000265284019],
                                   'price/fee/total unit': ['BTC']}
    correct_coinbase_pro_df = pd.DataFrame(correct_coinbase_pro_format)

    correct_dfs_dict = {'coinbase': correct_coinbase_df,
                       'coinbase_pro': correct_coinbase_pro_df}

    return correct_dfs_dict


def col_names_correct(user_df, correct_df):
    """ Check columns in the user input are named correctly and located at the expected index"""
    cor_cols = correct_df.columns
    user_cols = user_df.columns

    for col_index in range(0, len(cor_cols) - 1):
        if cor_cols[col_index] == user_cols[col_index]:
            pass
        else:
            return False  # If a user column does not match the correct column name
        return True


def check_column_names(user_df, correct_df, exchange):
    """ calls on the col_names_correct method to ensure column names are correct"""
    if col_names_correct(user_df, correct_df):
        return user_df
    else:
        print(exchange + " data has incorrect column names, please ensure that the correct file has been uploaded")
        sys.exit(1)


def file_can_be_read(path, skiprows, exchange):
    """ checks that the file can be loaded and is of the correct format: csv """
    try:
        df = pd.read_csv(path, skiprows=skiprows)
    except RowError:
        print(exchange + " data is not correct, please ensure that it is a csv file")
        sys.exit(1)

    return df


def validate(user_input):
    """ Main function that calls on the check_loaded, and check_column_names methods"""

    user_dfs_dict = {}

    correct_dfs_dict = get_correct_dfs_dict()

    if "coinbase" in user_input:
        cb_df = file_can_be_read(user_input["coinbase"], 7, "coinbase")
        cb_df = check_column_names(cb_df, correct_dfs_dict['coinbase'], "coinbase")

        user_dfs_dict["coinbase"] = cb_df

    if "coinbase_pro" in user_input:
        cb_pro_df = file_can_be_read(user_input['coinbase_pro'], 0, "coinbase_pro")
        cb_pro_df = check_column_names(cb_pro_df, correct_dfs_dict['coinbase_pro'], "coinbase pro")

        user_dfs_dict["coinbase_pro"] = cb_pro_df

    return user_dfs_dict
