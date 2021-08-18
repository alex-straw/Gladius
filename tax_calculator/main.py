# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
import time
import load_files
import uniform_coinbase_pro
import uniform_coinbase
import evaluate_in_fiat
import crypto_USD_portfolios
import same_day_rule
import thirty_day_s104_rules


file_paths = {'coinbase': r"C:\Users\alexa\Desktop\user_spreadsheets\cb.csv",
              'coinbase_pro': r"C:\Users\alexa\Desktop\user_spreadsheets\cb_pro.csv",
              'BTC': r"C:\Users\alexa\Desktop\price_data\Binance_BTCUSDT_minute.csv",
              'ETH': r"C:\Users\alexa\Desktop\price_data\Binance_ETHUSDT_minute.csv",
              'results': r"C:\Users\alexa\Desktop\output_testing"
              }


def main(file_paths):
    t = time.time()

    # Load trading data from excel spreadsheets
    coinbase_df, coinbase_pro_df = load_files.load_trading_data(file_paths['coinbase'], file_paths['coinbase_pro'])

    # Standardise portfolios prior to data merge
    # FORMAT: | dd/mm/yyyy | unix | side | c1 name | c1 size | c2 name | c2 size | c2 size USD |
    coinbase_df = uniform_coinbase.organise_data(coinbase_df)
    coinbase_pro_df = uniform_coinbase_pro.organise_data(coinbase_pro_df)

    portfolio_array = [coinbase_pro_df, coinbase_df]

    # Merge portfolios
    df = pd.concat(portfolio_array)

    # Get total value of transaction and token prices in USD and sort chronologically by unix time
    df = evaluate_in_fiat.get_prices(df, file_paths)
    df = df.sort_values(by=["date"])
    df = df.reset_index(drop=True)

    # Separate into many data frames - one for each unique currency traded
    cryptos_traded, crypto_dict = crypto_USD_portfolios.make_portfolios(df, file_paths)

    # Handle all same day transactions and settle each day in terms of the net trade type: acquisition or disposal
    crypto_dict = same_day_rule.group_transactions(crypto_dict)

    # Handle 30 day rule and S104 rules
    crypto_dict = thirty_day_s104_rules.match_crypto(crypto_dict)

    # Save merged portfolio to local directory
    crypto_dict['BTC'].to_csv(file_paths['results'] + "\BTC_priced.csv")

    print(time.time() - t)


if __name__ == '__main__':
    main(file_paths)
