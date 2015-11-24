'''
This module provides functions to read and write Table datasets.

:author: Juan Morales
'''

import pandas as pd
import json
import os
import collections

from indyva.dataset.table import Table
from indyva import for_json_bridge

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
                schema = json.load(f, object_pairs_hook=collections.OrderedDict)
        else:  # Assume the string is the json representation
            schema = json.loads(schema, object_pairs_hook=collections.OrderedDict)

    df = pd.read_csv(filepath, *args, **kwargs)
    df.fillna(fillna, inplace=True)
    table = Table(name=table_name, schema=schema)
    table.data(df)
    return table



def write_csv(table, filepath, schema=None, *args, **kwargs):
    '''
    This function writes the data of the provided table into a CSV file. If a
    schema is also provided then it is written in the same directory, ussing the
    same name of the file but with "_schema.json" suffix.

    :param Table table: The table you want to write to csv

    :param str filepath: The path where the csv file is going to be located.
    The string could be a URL. Valid URL schemes include http, ftp, s3,
    and file. For file URLs, a host is expected. For instance, a local
    file could be file://localhost/path/to/table.csv

    :param Schema schema: The schema associated with the table. You usually
    use table.schema as this argument. If None then no schema is written.

    :return: None

    This functions is a simple wrapper for `pandas.DataFrame.to_csv` function,
    and so any optional provided arguments are going to be bypassed to
    `pandas.DataFrame.to_csv` function.
    '''
    data = table.get_data()
    pd.DataFrame(data).to_csv(filepath, index=False, encoding='utf-8', *args, **kwargs)
    if schema is not None:
        with open(filepath.replace(".csv", "_schema.json"), "w") as fd:
            fd.write(json.dumps(schema, default=for_json_bridge))
    return None
