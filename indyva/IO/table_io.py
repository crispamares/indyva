'''
This module provides functions to read and write Table datasets.

:author: Juan Morales
'''

import pandas as pd
import json
import os

from indyva.dataset.table import Table


def read_csv(table_name, filepath, schema=None, fillna="NaN", *args, **kwargs):
    '''
    This function creates a table with the data from a CSV file.
    The schema is inferred from data.

    :param str table_name: The name you want to give to the new table

    :param str filepath: The path where the csv file is located.  The
    string could be a URL. Valid URL schemes include http, ftp, s3,
    and file. For file URLs, a host is expected. For instance, a local
    file could be file://localhost/path/to/table.csv

    :param str schema: The schema to use in the creation of the
    table. If None then the schema will be infered from the data. The
    string could be a schema's json representation or the local
    filepath of the json file that conatins the schema information.

    :return: Table

    This functions is a simple wrapper for `pandas.read_csv` function,
    and so any optional provided arguments are going to be bypassed to
    `pandas.read_csv` function.

    Common parameters are:

    sep : string, default ','
        Delimiter to use. If sep is None, will try to automatically determine
        this. Regular expressions are accepted.
    names : array-like
        List of column names to use. If file contains no header row, then you
        should explicitly pass header=None
    prefix : string or None (default)
        Prefix to add to column numbers when no header, e.g 'X' for X0, X1, ...
    na_values : list-like or dict, default None
        Additional strings to recognize as NA/NaN. If dict passed, specific
        per-column NA values
    true_values : list
        Values to consider as True
    false_values : list
        Values to consider as False
    keep_default_na : bool, default True
        If na_values are specified and keep_default_na is False the default NaN
        values are overridden, otherwise they're appended to
    '''
    if schema is not None:
        if os.path.exists(schema):
            with open(schema) as f:
                schema = json.load(f)
        else:  # Assume the string is the json representation
            schema = json.loads(schema)

    df = pd.read_csv(filepath, *args, **kwargs)
    df.fillna(fillna, inplace=True)
    table = Table(name=table_name, schema=schema)
    table.data(df)
    return table
