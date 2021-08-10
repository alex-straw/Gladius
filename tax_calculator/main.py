# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
import load_files


def main():
    coinbase_path = r"C:\Users\alexa\Desktop\user_spreadsheets\cb.csv"  # r indicates raw string
    coinbase_pro_path = r"C:\Users\alexa\Desktop\user_spreadsheets\cb_pro.csv"
    coinbase_df,coinbase_pro_df = load_files.load_trading_data(coinbase_path,coinbase_pro_path)


if __name__ == '__main__':
    main()