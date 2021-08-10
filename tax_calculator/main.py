# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
import load_files
import uniform_coinbase
import uniform_coinbase_pro


def main():
    coinbase_path = r"C:\Users\alexa\Desktop\user_spreadsheets\cb.csv"  # r indicates raw string
    coinbase_pro_path = r"C:\Users\alexa\Desktop\user_spreadsheets\cb_pro.csv"

    results_path = r"C:\Users\alexa\Desktop\output_testing"  # Local output path for spreadsheets

    # Load trading data from excel spreadsheets
    coinbase_df, coinbase_pro_df = load_files.load_trading_data(coinbase_path,coinbase_pro_path)

    # Standardise portfolios for merge
    # | dd/mm/yyyy | unix | side | c1 name | c1 size | c2 name | c2 size | c2 size USD |

    coinbase_df = uniform_coinbase.organise_data(coinbase_df)
    coinbase_pro_df = uniform_coinbase_pro.organise_data(coinbase_pro_df)

    coinbase_df.to_csv(results_path + "\cb.csv")
    coinbase_pro_df.to_csv(results_path + "\cb_pro.csv")


if __name__ == '__main__':
    main()