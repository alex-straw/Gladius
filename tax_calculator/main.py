# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
import load_files
import uniform_coinbase
import uniform_coinbase_pro
import fiat_transactions


def main():
    coinbase_path = r"C:\Users\alexa\Desktop\user_spreadsheets\cb.csv"  # r indicates raw string
    coinbase_pro_path = r"C:\Users\alexa\Desktop\user_spreadsheets\cb_pro.csv"

    results_path = r"C:\Users\alexa\Desktop\output_testing"  # Local output path for spreadsheets

    # Load trading data from excel spreadsheets
    coinbase_df, coinbase_pro_df = load_files.load_trading_data(coinbase_path, coinbase_pro_path)

    # Standardise portfolios prior to data merge
    # FORMAT: | dd/mm/yyyy | unix | side | c1 name | c1 size | c2 name | c2 size | c2 size USD |
    coinbase_df = uniform_coinbase.organise_data(coinbase_df)
    coinbase_pro_df = uniform_coinbase_pro.organise_data(coinbase_pro_df)

    # Save updated portfolios to local directory
    coinbase_df.to_csv(results_path + "\cb.csv")
    coinbase_pro_df.to_csv(results_path + "\cb_pro.csv")

    # Merge portfolios and sort chronologically by unix time
    df = pd.concat([coinbase_df, coinbase_pro_df])
    df = df.sort_values(by=["unix"])
    df = df.reset_index(drop=True)

    # Get total value of transaction and token prices in USD
    df = fiat_transactions.get_prices(df)

    # Save merged portfolio to local directory
    df.to_csv(results_path + "\portfolio.csv")


if __name__ == '__main__':
    main()
