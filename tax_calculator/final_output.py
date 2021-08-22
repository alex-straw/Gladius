import pandas as pd
import numpy as np
from datetime import datetime

tax_years = {'2019_start_date': '2019-04-06 00:00:00+00:00',
             '2019_end_date': '2020-04-05 23:59:59+00:00',
             '2020_start_date': '2020-04-06 00:00:00+00:00',
             '2020_end_date': '2021-04-05 23:59:59+00:00',
             '2021_start_date': '2021-04-06 00:00:00+00:00',
             '2021_end_date': '2022-04-05 23:59:59+00:00',
             '2022_start_date': '2022-04-06 00:00:00+00:00',
             '2022_end_date': '2023-04-05 23:59:59+00:00'
             }


class TaxObj(object):
    """ Tax summary for each crypto asset traded during the financial year """

    def __init__(self, name):
        self.name = name

        self.total_cap_losses = 0
        self.total_cap_gains = 0

        self.same_day_cap_losses = 0
        self.same_day_cap_gains = 0

        self.thirty_day_cap_losses = 0
        self.thirty_day_cap_gains = 0

        self.s104_cap_losses = 0
        self.s104_cap_gains = 0


# item = 'day_trading'
# direction = 'cap_losses'
#
# link = TaxObj("link")
#
# attribute = item + "_" + direction
#
# value = 50
# setattr(link, attribute, 50)

def sum_gains(name, df, rules, directions):
    name = TaxObj(name)  # Create an instance of TaxObj for the given crypto asset

    for rule in rules:
        for direction in directions:
            attribute = rule + direction


def retrieve_data_tax_year(df, start, end):
    mask = (df['date'] > start) & (df['date'] <= end)
    df_tax_year = df.loc[mask]

    return df_tax_year


def get_taxes(crypto_dict, tax_year):

    rules = ["same_day_", "thirty_day_", "s104_"]
    directions = ["cap_losses", "cap_gains"]

    for name in crypto_dict:
        print(crypto_dict[name]['date'])
        #df_tax_year = retrieve_data_tax_year(crypto_dict[name], start, end)
        sum_gains(name, df_tax_year, rules, directions)

    return crypto_dict
