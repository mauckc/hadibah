# Shelter data frame python pandas
# Python 2.7 file for processing csv files of animal intake reports
# File being read: "UCDavis_KE_5- 1-1-2012-5-31-2018.xls"
from datetime import datetime
import numpy as np
import time
import pandas as pd
#import matplotlib.pyplot as plt
import math



if __name__ == '__main__':
    # Read csv to file using pandas
    # inAndOutData_path = "allJoinedProcessedDataAAC.csv"
    inAndOutData_path = "safe_noheaders_allJoinedProcessedDataAAC.csv"

    df = pd.read_csv(inAndOutData_path)



    # # Process columns
    # df.columns = [ col.lower() for col in df.columns]
    # df.columns = [ col.replace(':','') for col in df.columns]
    # df.columns = [ col.replace(' ','_') for col in df.columns]
    # df.columns = [ col.replace('\n','') for col in df.columns]
    # df.columns = [ col.replace('\t','') for col in df.columns]
    # df = df.rename(columns={ df.columns[0]: "index" })
    #
    # # Calculate New Fields LOS and Days Old
    # df['los'] = (pd.to_datetime(df.outcome_date) - pd.to_datetime(df.intake_date))/ np.timedelta64(1, 'D')
    # df['days_old'] = (pd.to_datetime(df.intake_date) - pd.to_datetime(df.dob))/ np.timedelta64(1, 'D')

    headers_inAndOut = list(df.columns.values)
    print(headers_inAndOut)
    print( np.shape(df) )
    print(df.head())
    # df['los'] = [ pd.to_datetime(row['datetime']) -  pd.to_datetime(row['outcome_datetime']) for row in df ]
    df['days_old'] = pd.to_datetime(df['datetime']) -  pd.to_datetime(df['outcome_date_of_birth'])
    df['days_old'] = [ timedel.days for timedel in df['days_old']]

    print(df['days_old'])

    los_value_counts = df['los'].value_counts()
    print(los_value_counts[:10])

    print(df.head())


    # Modify animal type and save species
    df['species'] = df['animal_type']
    oldSpecs = df['animal_type']
    daysOld = df['days_old']
    newSpecs = []

    for i in range(len(df)):
        if daysOld.values[i] < 153: #*8.64*math.pow(10.0,13.0)): # 8.64e+13 nanoseconds per day
            # print "line 84"
            if oldSpecs.values[i] == "Cat":
                newSpecs.append("Kitten")
            elif oldSpecs.values[i] == "Dog":
                newSpecs.append("Puppy")
            else:
                # Juvenile Wildlife doesn't change
                newSpecs.append(oldSpecs.values[i])
        else:
            # Adults remains unchanged
            newSpecs.append(oldSpecs.values[i])

    ### Update Data Frame
    df['animal_type'] = newSpecs

    headers = ['intake_index', 'animal_id', 'name', 'datetime', 'monthyear', 'found_location',
     'intake_type', 'intake_condition', 'animal_type', 'sex_upon_intake',
     'age_upon_intake', 'breed', 'color','los', 'outcome_index',
     'outcome_animal_id', 'outcome_name', 'outcome_datetime', 'outcome_monthyear',
     'outcome_date_of_birth', 'outcome_type', 'outcome_subtype',
     'outcome_animal_type', 'sex_upon_outcome', 'age_upon_outcome',
     'outcome_breed', 'outcome_color','species']

    df.to_csv('animalsAAC_{}.csv'.format(datetime.now().strftime('%Y-%m-%d_%H_%M_%S')), index=False)
