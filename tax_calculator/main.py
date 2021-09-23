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
              'tax_year': '2020',
              'tax_allowance': 12300}


def output_demo(summary, parameters):
    print("total capital losses in " + parameters['tax_year'] + ": £" + str(summary["losses"]))
    print("total capital gains in " + parameters['tax_year'] + ": £" + str(summary["gains"]))

    net = summary["losses"] + summary["gains"]
    print("net: £" + str(net))

    if net < 0:
        print("losses of £" + str(net) + " can be applied to your gains in the next 4 years to reduce tax owed")
    else:
        if parameters["tax_allowance"] - net > 0:
            print("£0 in tax owed, remaining tax free allowance for year = " + str(parameters["tax_allowance"] - net))
        else:
            taxable_amount = net - parameters["tax_allowance"]
            print("tax free allowance used, carry over previous losses, or you must pay tax on " + taxable_amount)


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

    # Separate complete df into many specific portfolios that contain only a single crypto-asset (all in GBP)
    cryptos_traded, crypto_dict = make_crypto_specific_portfolios.make_portfolios(df, file_paths)

    crypto_dict = apply_UK_tax_rules.master_func(crypto_dict)
    crypto_dict['ALGO'].to_csv(file_paths['results'] + "\ALGO_traded.csv")

    # Input crypto dict, output a dictionary with ["gains"] and ["losses"]
    summary = final_output.get_taxes(crypto_dict, parameters['tax_year'])

    output_demo(summary, parameters)
    print("total time: " + str(time.time() - t) + "s")


if __name__ == '__main__':
    main(file_paths, parameters)
