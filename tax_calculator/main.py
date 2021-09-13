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
import final_output
import uniform_exchange_data

file_paths = {'testing_cb_pro': r"C:\Users\alexa\Desktop\user_spreadsheets\scarlett_cb_pro.csv",
              'GOV_example_6': r"C:\Users\alexa\Desktop\user_spreadsheets\EXAMPLE_6_GOV.csv",
              'coinbase': r"C:\Users\alexa\Desktop\user_spreadsheets\cb.csv",
              'coinbase_pro': r"C:\Users\alexa\Desktop\user_spreadsheets\cb_pro.csv",
              'BTC': r"C:\Users\alexa\Desktop\price_data\Binance_BTCUSDT_minute.csv",
              'ETH': r"C:\Users\alexa\Desktop\price_data\Binance_ETHUSDT_minute.csv",
              'results': r"C:\Users\alexa\Desktop\output_testing"
              }

parameters = {'home_currency': 'GBP',
              'tax_year': '2021'}


def main(file_paths, parameters):
    t = time.time()

    # Load trading data from excel spreadsheets
    coinbase_df = load_files.coinbase(file_paths['coinbase'])

    coinbase_pro_df = load_files.coinbase_pro(file_paths['coinbase_pro'])

    # Standardise portfolios prior to data merge
    coinbase_df = uniform_exchange_data.coinbase_main(coinbase_df)
    coinbase_pro_df = uniform_exchange_data.coinbase_pro_main(coinbase_pro_df)

    portfolio_array = [coinbase_pro_df, coinbase_df]

    # Merge portfolios
    df = pd.concat(portfolio_array)

    # Get total value of transaction and token prices in USD and sort chronologically by unix time

    df = evaluate_in_fiat.get_prices(df, file_paths, parameters)
    df.to_csv(file_paths['results'] + "\PRICED.csv")

    df = df.sort_values(by=["date"])
    df = df.reset_index(drop=True)

    # Separate into many data frames - one for each unique currency traded
    # Currencies are converted into USD first as this is the market with the highest volume
    # Higher volume typically improves price accuracy, and reduces spread
    cryptos_traded, crypto_dict = crypto_USD_portfolios.make_portfolios(df, file_paths)

    crypto_dict['BTC'].to_csv(file_paths['results'] + "\BTC_PRE.csv")

    # Handle all same day transactions and settle each day in terms of the net trade type: acquisition or disposal
    crypto_dict = same_day_rule.group_transactions(crypto_dict)

    # Handle 30 day rule and S104 rules
    crypto_dict = thirty_day_s104_rules.final_pass(crypto_dict)
    crypto_dict['BTC'].to_csv(file_paths['results'] + "\BTC.csv")

    summary = final_output.get_taxes(crypto_dict, parameters['tax_year'])

    print("total time: " + str(time.time() - t) + "s")


if __name__ == '__main__':
    main(file_paths, parameters)
