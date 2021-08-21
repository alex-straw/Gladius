import pandas as pd
import numpy as np
import datetime as datetime

tax_years = {'2019_start_date': pd.to_datetime('2019-04-06 00:00:00'),
             '2019_end_date': pd.to_datetime('2020-04-05 23:59:59'),
             '2020_start_date': pd.to_datetime('2020-04-06 00:00:00'),
             '2020_end_date': pd.to_datetime('2021-04-05 23:59:59'),
             '2021_start_date': pd.to_datetime('2021-04-06 00:00:00'),
             '2021_end_date': pd.to_datetime('2022-04-05 23:59:59'),
             '2022_start_date': pd.to_datetime('2022-04-06 00:00:00'),
             '2022_end_date': pd.to_datetime('2023-04-05 23:59:59')
             }


def get_taxes(crypto_dict, tax_year):

    start = tax_years[tax_year + "_start_date"]
    end = tax_years[tax_year + "_end_date"]

    return crypto_dict
