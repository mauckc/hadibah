





import numpy as np
import pandas as pd
from werkzeug.contrib.cache import SimpleCache
import os
cache = SimpleCache()
from datetime import date
oldcolors = {
    'Blue': '#1f77b4',
    'Orange': '#ff7f0e',
    'Green': '#2ca02c',
    'Red': '#d62728',
    'Purple': '#9467bd',
}

colors = {
    'Red': '#B41f77',
    'Orange': '#77B41F',
    'Green': '#1FB477',
    'Blue': '#1f77b4',
    'Purple': '#771FB4',
}

def readSC(nrows=None):

    df = cache.get('animalDB')
    plot_columns = cache.get('animalCols')

    if (df is None) or (plot_columns is None):
        plot_columns = ['intake_index', 'animal_id', 'name', 'datetime', 'monthyear', 'found_location',
                 'intake_type', 'intake_condition', 'animal_type', 'sex_upon_intake',
                 'age_upon_intake', 'breed', 'color','los', 'outcome_index',
                 'outcome_animal_id', 'outcome_name', 'outcome_datetime', 'outcome_monthyear',
                 'outcome_date_of_birth', 'outcome_type', 'outcome_subtype',
                 'outcome_animal_type', 'sex_upon_outcome', 'age_upon_outcome',
                 'outcome_breed', 'outcome_color']
        if not os.path.exists('./data/animalsAAC.csv'):
            print("[INFO]: animalsAAC.tsv does not exist...\n[INFO]: looking for other file extensions...")
            if os.path.exists('data/animalsAAC.xls'):
                print("[INFO]: animalsAAC.xls does exist...\n[INFO]: using this file...")
                df = pd.read_excel('./data/animalsAAC.xls')
                df.to_csv('./data/animalsAAC.tsv', sep='\t')
                df.to_csv('./data/animalsAAC.csv')
            elif os.path.exists('./data/animalsAAC.csv'):
                print("[INFO]: animalsAAC.xls does not exist...\n[INFO]: using animalsAAC.csv file instead...")
                df = pd.read_csv('./data/animalsAAC.csv')
                df.to_csv('./data/animalsAAC.tsv', sep='\t')
            else:
                print("[Err]: No data in the directory: './data/' i.e. add the data file to ./data/animalsAAC.csv")
        else:
            df = pd.read_table('./data/animalsAAC.csv')

        # df = pd.read_csv('./data/animalsAAC.csv')
        # df = pd.read_excel('./data/animals.xls')
        df.to_csv('./data/animalsAAC.tsv',sep='\t')

        df = pd.read_csv('./data/animalsAAC.csv')
        preprocess_shape = df.shape
        print(preprocess_shape)

        value_to_check = pd.Timestamp(date.today().year, 1, 1)
        df['datetime'] = [ pd.Timestamp(t) for t in df['datetime'] ]
        filter_mask = df['datetime'] < value_to_check
        df[filter_mask]
        # df = df[df['datetime'] > pd.to_datetime('2017-01-01','%Y-%m-%d')]
        df['name'] = unicode(df['name'].str.replace('*',''))
        df['outcome_name'] = unicode(df['outcome_name'].str.replace('*',''))
        cache.set('animalDB', df, timeout=5*60)
        cache.set('animalCols', plot_columns, timeout=5*60)

        if nrows is not None:
            return df.loc[:nrows-1, :], plot_columns

    plot_columns = df.columns

    return df, plot_columns

def table_convert(fmt="csv"):
    """Convert the SC data into different formats.
    To make available for download.
    """
    # others netcdf, fits?
    # https://pandas.pydata.org/pandas-docs/stable/io.html
    if fmt not in ['tsv', 'csv', 'hdf','xls']:
        raise NotImplementedError("Conversion format to {} not available.".format(fmt))
    name = "data/animalsAAC.{}".format(fmt)
    if fmt is "csv":  # This is the standard
        pass
    else:
        df = pd.read_table('data/animalsAAC.csv')
        if fmt == "hdf":
            df.to_hdf(name, key="animals", mode="w", format='table')
        elif fmt == "tsv":
            df.to_csv(name, sep=",", index=False)

def get_default(value, default, dtype, na_value='...'):
    if isinstance(value, dtype) and (value != na_value):
        return value
    else:
        return default
