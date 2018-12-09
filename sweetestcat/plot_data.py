import numpy as np
import pandas as pd
import csv
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()

# df = pd.read_csv('./data/010116 through 100118.csv')
def readAnimalData():
    """Read the exoplanet.eu database from the 'data' folder and store as
    pandas DataFrame
    ['A1433734', 'DOG', 'N', 'MALTESE', '01/01/2015', '1', '0.00', '1.1', 'STRAY', 'SANTA ANA', '01/01/2016', '11:36 am', 'NORMAL', 'SANTA ANA.1', 'FLOWER/CHESTNUT', 'ADOPTION', 'DOG 5', '01/08/2016', ' 2:53 pm', 'Unnamed: 19']
    """
    df = cache.get('animalDB')
    if df is None:
        input_headers = ['animal_id','animal_type','sex','breed','DOB','years_old','months_old','intake_total','intake_type','intake_subtype','intake_date','intake_time','intake_condition','intake_jurisdiction','crossing','outcome_type','outcome_subtype','outcome_date','outcome_time','outcome_condition']
        df = pd.read_csv('./data/010116 through 100118.csv', header=None, names=input_headers, engine='c')
        idx = np.zeros(len(df), dtype=bool)
        # for pl in 'abcdefgh':
        #     idx = idx | df['plName'].str.endswith(' {}'.format(pl))
        # df.loc[idx, 'stName'] = df.loc[idx, 'plName'].str[:-2]
        # df.loc[~idx, 'stName'] = df.loc[~idx, 'plName']
        # df['plDensity'] = plDensity(df['plMass'], df['plRadius'])  # Add planet density
        cache.set('animalDB', df, timeout=5*60)
    return df

def filterSpecies(df):
    df = df[(df['animal_type'] == 'CAT') | (df['animal_type'] =='DOG')| (df['animal_type'] =='KITTEN') | (df['animal_type'] =='PUPPY')]
    return df

def filterDEADIntake(df):
    df = df[(df['intake_type'] != 'DEAD') & (df['intake_type'] !='DISPOSAL') & (df['intake_type'] !='DEADONARR') &(df['intake_subtype'] != 'DEAD') & (df['intake_subtype'] !='DISPOSAL') & (df['intake_subtype'] !='DEADONARR') & (df['intake_condition'] != 'DEAD') & (df['intake_condition'] !='DISPOSAL') & (df['intake_condition'] !='DEADONARR') & (df['outcome_condition'] !='DEADONARR')]
    return df

def printCounts(series):
    series_count = series.value_counts()
    print('[START]:' + series_count.name + ' ----------VVVVVVVV')
    print(series_count)
    print('[END]:' + series_count.name+ ' ----------^^^^^^^^^^^^^^')

rawdata = readAnimalData()
specsdata = filterSpecies(rawdata)
dat = filterDEADIntake(specsdata)

print(dat.head())
print(dat.columns)

printCounts(dat['intake_type'])
printCounts(dat['intake_subtype'])
printCounts(dat['intake_condition'])
printCounts(dat['outcome_type'])
printCounts(dat['outcome_subtype'])
printCounts(dat['outcome_condition'])
printCounts(dat['intake_jurisdiction'])
