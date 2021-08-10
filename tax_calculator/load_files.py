# -*- coding: utf-8 -*-
import glob
import os
import pandas as pd

"""
Created on Sunday August 09 12:34:00 2021
Author: Alex Straw
Description:
    Load files from a local folder
"""


def load_trading_data(coinbase_path,coinbase_pro_path):
    coinbase_df = pd.read_csv(coinbase_path)
    coinbase_pro_df = pd.read_csv(coinbase_pro_path)

    return coinbase_df,coinbase_pro_df


