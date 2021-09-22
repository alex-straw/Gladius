# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
import time

import user_input_validation
import get_standard_currency
import make_crypto_specific_portfolios
import apply_same_day_rule
import apply_thirty_day_s104_rules
import final_output
import uniform_exchange_data
import apply_UK_tax_rules

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

    input_dict = {"coinbase_pro": file_paths['coinbase_pro'], "coinbase": file_paths['coinbase']}  # Default input

    user_df_dict = user_input_validation.validate(input_dict)  # Load files and validate if user input is correct

    portfolio_array = []

    # Standardise coinbase data if the user has provided it
    if "coinbase" in user_df_dict:
        user_df_dict["coinbase"] = uniform_exchange_data.coinbase_main(user_df_dict["coinbase"])
        portfolio_array.append(user_df_dict["coinbase"])

    # Standardise coinbase pro data if the user has provided it
    if "coinbase_pro" in user_df_dict:
        user_df_dict["coinbase_pro"] = uniform_exchange_data.coinbase_pro_main(user_df_dict["coinbase_pro"])
        portfolio_array.append(user_df_dict["coinbase_pro"])

    # Merge portfolios
    df = pd.concat(portfolio_array)

    # Assign minute precise BTC/ETH/USD/EUR/USDC -TO-> GBP exchange rates for each transaction.
    # This is required to get consistent gain/loss information during bulk calculations.
    df = get_standard_currency.get_prices(df, file_paths)

    # Once priced all transactions are sorted chronologically
    df = df.sort_values(by=["date"])
    df = df.reset_index(drop=True)

    # Separate into many data frames - one for each unique currency traded
    # Currencies are converted into USD first as this is the market with the highest volume
    # Higher volume generally improves price accuracy, and reduces spread
    cryptos_traded, crypto_dict = make_crypto_specific_portfolios.make_portfolios(df, file_paths)
    #crypto_dict['ALGO'].to_csv(file_paths['results'] + "\ALGO_traded.csv")

    crypto_dict = apply_UK_tax_rules.master_func(crypto_dict)

    summary = final_output.get_taxes(crypto_dict, parameters['tax_year'])

    print("total time: " + str(time.time() - t) + "s")


if __name__ == '__main__':
    main(file_paths, parameters)
