# -*- coding: utf-8 -*-
"""
Created on Sunday August 09 12:34:00 2021
Author: Alex Straw
Description:
    Take Coinbase Pro fills data and output in the format:
    
    | dd/mm/yyyy | unix | side | c1 name | c1 size | c2 name | c2 size | c2 size USD |
"""

import pandas as pd
import numpy as np
import os
import re


def organise_data(df):
    return df