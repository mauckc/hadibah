





import numpy as np
import pandas as pd
from werkzeug.contrib.cache import SimpleCache
import os
cache = SimpleCache()

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
        plot_columns = ['index','animal_id','animal_type','sex','primary_bree','dob','secondary_','kennel_no','impound_no','intake_type','intake_subtype','intake_date','s_n_date','intake_cond','weight','weight_1_week','outcome_type','outcome_subtype','outcome_date','due_out_date','outcome_cond','location_1','location_1_date','location_2','location_2_date','behavior_cond','outcome_behavior_cond','euth_reason','intake_date_form_2']
        if not os.path.exists('./data/animals.tsv'):
            print("[INFO]: animals.tsv does not exist...\n[INFO]: looking for other file extensions...")
            if os.path.exists('data/animal.xls'):
                print("[INFO]: animals.xls does exist...\n[INFO]: using this file...")
                df = pd.read_excel('./data/animals.xls')
                df.to_csv('./data/animals.tsv', sep='\t')
                df.to_csv('./data/animals.csv')
            elif os.path.exists('./data/animal.csv'):
                print("[INFO]: animals.xls does not exist...\n[INFO]: using animal.csv file instead...")
                df = pd.read_csv('./data/animals.csv')
                df.to_csv('./data/animals.tsv', sep='\t')
            else:
                print("[Err]: No data in the directory: './data/' i.e. add the data file to ./data/animals.csv")
        else:
            df = pd.read_table('./data/animals.tsv')

        df = pd.read_excel('./data/animals.xls')
        df.to_csv('./data/animals.tsv',sep='\t')

        df = pd.read_table('./data/animals.tsv')
        preprocess_shape = df.shape
        print(preprocess_shape)

        # Process structure
        # df = df.dropna(how='all', axis=1)
        # df = df.dropna(how='all', axis=0)#, inplace=True)

        # Process columns
        df.columns = [ col.lower() for col in df.columns]
        df.columns = [ col.replace(':','') for col in df.columns]
        df.columns = [ col.replace(' ','_') for col in df.columns]
        df.columns = [ col.replace('\n','') for col in df.columns]
        df.columns = [ col.replace('\t','') for col in df.columns]
        df = df.rename(columns={ df.columns[0]: "index" })
        # df = df[0:1000]
        #df['flag'] = df['flag'] == 1  # Turn to bool
        # df['Vabs'] = absolute_magnitude(df['par'], df['Vmag'])
        # df['lum'] = list(map(luminosity, df['teff'], df['Vmag'], df['par']*1E-3, df['mass']))
        #df['Star'] = df['Star'].str.strip()
        # print(df.head())
        postprocess_shape = df.shape
        if postprocess_shape != preprocess_shape:
            # Save the data
            print("[INFO]: Preprocess Shape: {} != Postprocess Shape: {}".format(preprocess_shape, postprocess_shape))
            print("[INFO]: Changes have been made...\n[INFO]: Writing to'./data/animals.tsv'")
            df.to_csv('./data/animals.tsv',sep='\t')

        df = df[(pd.to_datetime(df['intake_date']) < pd.to_datetime('20181212'))]
        # # Generate missing link https://github.com/DanielAndreasen/SWEETer-Cat/issues/135
        # for impound_no in df.animal_id[df['outcome_date'].isnull()].values:
        #     df.loc[df['impound_no'] == impound_no, ['']] = generate_missing_link(animal)

        # Print all impound numbers that have outcome_dates that are null values
        # for impound_no in df.animal_id[df['outcome_date'].isnull()].values:
        #     print(impound_no)

        # breakdown_counts = []
        # for col in df.columns:
        #     breakdown_counts.append((col, df[col].value_counts()))
        # # print(breakdown_counts)
        # print(breakdown_counts[0][0])
        # print(breakdown_counts[0][1])
        # for col in breakdown_counts:
        #     print(col[0])
        #     print(col[1][0:10])

        # Calculate New Fields LOS and Days Old
        df['los'] = (pd.to_datetime(df.outcome_date) - pd.to_datetime(df.intake_date))/ np.timedelta64(1, 'D')
        df['days_old'] = (pd.to_datetime(df.intake_date) - pd.to_datetime(df.dob))/ np.timedelta64(1, 'D')
        df['los_1'] = (pd.to_datetime(df.location_1_date) - pd.to_datetime(df.intake_date))/ np.timedelta64(1, 'D')
        df['los_2'] = (pd.to_datetime(df.location_2_date) - pd.to_datetime(df.location_1_date))/ np.timedelta64(1, 'D')
        df['age_s_n_date'] = (pd.to_datetime(df.s_n_date) - pd.to_datetime(df.dob))/ np.timedelta64(1, 'D')
        df['weight_difference'] = df.weight_1_week - df.weight
        df['in_to_due_out_date_diff'] = (pd.to_datetime(df.due_out_date) - pd.to_datetime(df.intake_date))/ np.timedelta64(1, 'D')
        df['due_out_to_outcome_date_diff'] = (pd.to_datetime(df.outcome_date) - pd.to_datetime(df.due_out_date))/ np.timedelta64(1, 'D')

        df['los_1'] = df['los_1'].round(5)
        df['los_2'] = df['los_2'].round(5)
        df['in_to_due_out_date_diff'] = df['in_to_due_out_date_diff'].round(5)
        df['due_out_to_outcome_date_diff'] = df['due_out_to_outcome_date_diff'].round(5)
        df['weight_difference'] = df['weight_difference'].round(3)
        # Change Animal Type field based on days old metric
        oldSpecs = df['animal_type']
        daysOld = df['days_old']
        newSpecs = []

        for i in range(len(df)):
            if pd.to_timedelta(daysOld.values[i]) <= pd.to_timedelta(150): #*8.64*math.pow(10.0,13.0)): # 8.64e+13 nanoseconds per day
                # print "line 84"
                if oldSpecs.values[i] == "CAT":
                    newSpecs.append("KITTEN")
                elif oldSpecs.values[i] == "DOG":
                    newSpecs.append("PUPPY")
                else:
                    # Juvenile Wildlife doesn't change
                    newSpecs.append(oldSpecs.values[i])
            else:
                # Adults remains unchanged
                newSpecs.append(oldSpecs.values[i])

        ### Update Data Frame
        df['animal_type'] = newSpecs

        # print df['animal_type'].value_counts()
        #
        # print np.shape(df)
        #
        # print(df['los'].head())
        # print(df['weight'].head())
        # print(df['newspecs'])

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
    name = "data/animals.{}".format(fmt)
    if fmt is "tsv":  # This is the standard
        pass
    else:
        df = pd.read_table('data/animals.tsv')
        if fmt == "hdf":
            df.to_hdf(name, key="animals", mode="w", format='table')
        elif fmt == "csv":
            df.to_csv(name, sep=",", index=False)

def get_default(value, default, dtype, na_value='...'):
    if isinstance(value, dtype) and (value != na_value):
        return value
    else:
        return default