import pandas as pd
import numpy as np
from datetime import datetime

tax_years = {'2019_start_date': '2019-04-06',
             '2019_end_date': '2020-04-05',
             '2020_start_date': '2020-04-06',
             '2020_end_date': '2021-04-05',
             '2021_start_date': '2021-04-06',
             '2021_end_date': '2022-04-05',
             '2022_start_date': '2022-04-06',
             '2022_end_date': '2023-04-05'
             }


class TaxObj(object):
    """ Tax summary for each crypto asset traded during the financial year """
    """ Needs Work """

    def __init__(self, name):
        self.name = name

        self.total_cap_losses = 0
        self.total_cap_gains = 0

        self.same_day_cap_losses = 0
        self.same_day_cap_gains = 0

        self.thirty_day_cap_losses = 0
        self.thirty_day_cap_gains = 0

        self.s104_pool_cap_losses = 0
        self.s104_pool_cap_gains = 0

    def sum_totals(self):
        self.total_cap_losses = self.same_day_cap_losses + self.thirty_day_cap_losses + self.s104_pool_cap_losses
        self.total_cap_gains = self.same_day_cap_gains + self.thirty_day_cap_gains + self.s104_pool_cap_gains


def sum_gains(name, df, rules):
    name = TaxObj(name)  # Create an instance of TaxObj for the given crypto asset
    print(name)

    for rule in rules:
        column_name = "net_" + rule

        attr_loss = rule + "_cap_losses"
        attr_gain = rule + "_cap_gains"

        print(column_name)
        cap_losses = df[column_name][df[column_name] < 0].sum()
        cap_gains = df[column_name][df[column_name] > 0].sum()

        setattr(name, attr_loss, cap_losses)
        setattr(name, attr_gain, cap_gains)

    name.sum_totals()

    return name.total_cap_losses, name.total_cap_gains


def retrieve_data_tax_year(df, start, end):
    df = df[(df['date'] >= start) & (df['date'] <= end)]
    return df


def get_taxes(crypto_dict, tax_year):
    rules = ["same_day", "thirty_day", "s104_pool"]

    Objs = [TaxObj(name) for name in crypto_dict]

    start = tax_years[tax_year + '_start_date']
    end = tax_years[tax_year + '_end_date']

    total_cap_gains = 0
    total_cap_losses = 0

    for name in crypto_dict:

        pd.to_datetime(crypto_dict[name]['date'])

        df_tax_year = retrieve_data_tax_year(crypto_dict[name], start, end)

        if len(df_tax_year) > 0:  # If any trades took place for the crypto in the tax year
            cap_losses, cap_gains = sum_gains(name, df_tax_year, rules)

            total_cap_losses += cap_losses
            total_cap_gains += cap_gains

    print("total capital losses in " + tax_year + ": £" + str(total_cap_losses))
    print("total capital gains in " + tax_year + ": £" + str(total_cap_gains))

    return crypto_dict
