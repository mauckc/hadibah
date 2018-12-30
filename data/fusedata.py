# Shelter data frame python pandas
# Python 2.7 file for processing csv files of animal intake reports
# File being read: "UCDavis_KE_5- 1-1-2012-5-31-2018.xls"
from datetime import datetime
import numpy as np
import time
import pandas as pd
#import matplotlib.pyplot as plt
import math
# import pygame

if __name__ == '__main__':
    # Read csv to file using pandas
    intake_data_path = "Austin_Animal_Center_Intakes.csv"
    outcome_data_path = "Austin_Animal_Center_Outcomes.csv"
    stray_data_path = "Austin_Animal_Center_Stray_Map.csv"

    dfintake = pd.read_csv(intake_data_path)
    headers_intake = list(dfintake.columns.values)
    print(headers_intake)
    print( np.shape(dfintake) )

    # pygame.init()

    dfoutcome = pd.read_csv(outcome_data_path)
    headers_outcome = list(dfoutcome.columns.values)
    print(headers_outcome)
    print( np.shape(dfoutcome) )

    # print dimensions of our pandas dataframe
    print( np.shape(dfintake) )
    # current headers are:
    headers = list(dfintake.columns.values)
    print(headers)

    # print dimensions of our pandas dataframe
    print( np.shape(dfoutcome) )
    # current headers are:
    headers = list(dfoutcome.columns.values)
    print(headers)

    # Update the data file
    # Remove empty rows
    dfintake = dfintake.dropna(how='all',axis=0)
    dfintake = dfintake.dropna(how='all', axis=1)

    dfoutcome = dfoutcome.dropna(how='all',axis=0)
    dfoutcome = dfoutcome.dropna(how='all', axis=1)

    # Fix column strings... still need to output without an index
    dfintake.columns = [x.lower() for x in dfintake.columns]
    dfintake.columns = [x.replace(' ','_') for x in dfintake.columns]
    dfintake.columns = [x.replace('\n','') for x in dfintake.columns]
    dfintake.columns = [x.replace('/','_') for x in dfintake.columns]
    # print dfintake.columns

    dfoutcome.columns = [x.lower() for x in dfoutcome.columns]
    dfoutcome.columns = [x.replace(' ','_') for x in dfoutcome.columns]
    dfoutcome.columns = [x.replace('\n','') for x in dfoutcome.columns]
    dfoutcome.columns = [x.replace('/','_') for x in dfoutcome.columns]
    ## Change headers of outcome file in order to have unique fields
    cols = []
    for col in dfoutcome.columns:
        if 'out' in col:
            cols.append(col)
        else:
            cols.append(''.join(('outcome_', col)))
    print(cols)
    dfoutcome.columns = cols
    print(dfoutcome.columns)
    print(headers_outcome)
    print( np.shape(dfoutcome) )
    # Drop out animals who have no outcome date
    dfoutcome = dfoutcome[dfoutcome.outcome_datetime.notnull()]
    # Get ids that are in both intake and outcome data sets
    animal_ids = set(dfintake['animal_id']) & set(dfoutcome['outcome_animal_id'])

    print('# of Animal IDs in both sets: %d' % (len(animal_ids),))
    print('# of rows in dfoutcome: %d' % (len(dfoutcome),))
    # dfout = dfoutcome.loc[dfoutcome['animal_id'].isin(animal_ids)]
    # print(len(dfout))
    # print dfout
    # dfoutcome = dfoutcome.loc[dfoutcome['outcome_animal_id'].isin(animal_ids)]
    # dfintake = dfintake.loc[dfintake['datetime']<pd.to_datetime('20180601')]
    outdf = pd.DataFrame(columns=np.concatenate((dfintake.columns,dfoutcome.columns), axis=None))

    writer = pd.ExcelWriter('allJoinedProcessedDataAAC.xls', index=False)



    headers = np.concatenate((list(dfintake.columns),list(dfoutcome.columns)))#, axis=None)
    print(headers)
    # df = pd.DataFrame(columns=headers)
    index_animal_id = 0
    inAndOutData = []
    numiter = 0

    dfintake = dfintake.sort_values(by=['animal_id'], ascending=False)

    start_time = time.time()
    for animal_id, datetime, intake_index in zip(dfintake['animal_id'],dfintake['datetime'],dfintake[dfintake.columns.values[0]]):

        # for event in pygame.event.get():
        #     if event.type == pygame.K_DOWN:
        #             outframe = pd.DataFrame(inAndOutData, columns=['intake_index', 'animal_id', 'name', 'datetime', 'monthyear', 'found_location',
        #              'intake_type', 'intake_condition', 'animal_type', 'sex_upon_intake',
        #              'age_upon_intake', 'breed', 'color','los', 'outcome_index',
        #              'outcome_animal_id', 'outcome_name', 'outcome_datetime', 'outcome_monthyear',
        #              'outcome_date_of_birth', 'outcome_type', 'outcome_subtype',
        #              'outcome_animal_type', 'sex_upon_outcome', 'age_upon_outcome',
        #              'outcome_breed', 'outcome_color'])
        #             outframe.to_csv('safe_headers_allJoinedProcessedDataAAC.csv',index=False)
        #             needsave = False

        if numiter % 1000 == 1:
            outframe = pd.DataFrame(inAndOutData)
            outframe.columns = ['intake_index', 'animal_id', 'name', 'datetime', 'monthyear', 'found_location','intake_type', 'intake_condition', 'animal_type', 'sex_upon_intake','age_upon_intake', 'breed', 'color', 'outcome_index','outcome_animal_id', 'outcome_name', 'outcome_datetime', 'outcome_monthyear','outcome_date_of_birth', 'outcome_type', 'outcome_subtype','outcome_animal_type', 'sex_upon_outcome', 'age_upon_outcome','outcome_breed', 'outcome_color']
            outframe.to_csv('./processed-data/safe_{}_allJoinedProcessedDataAAC.csv'.format(numiter),index=False)
            # needsave = False

        # print(index_animal_id)
        index_animal_id += 1
        # print(''.join((animal_id,' ',datetime.strftime('%Y-%m-%d'))))
        # print(''.join((animal_id,' ',datetime.strftime('%m/%d/%Y'))))
        dfIntakesThisAnimal = dfintake[(dfintake['animal_id'] == animal_id)]
        dfThisIntakeThisAnimal = dfintake[(dfintake['animal_id']  == animal_id) & (dfintake['datetime'] == datetime) & (dfintake['unnamed:_0'] == intake_index)]

        # if len(dfThisIntakeThisAnimal) > 1:
        #     print(len(dfThisIntakeThisAnimal))
        #     print('[ERR]: Multiple Intakes with same ID and same intake date')
        #     dfThisIntakeThisAnimal = dfThisIntakeThisAnimal[0]

        dfOutcomesThisAnimal = dfoutcome[(dfoutcome['outcome_animal_id']  == animal_id)]
        # if dfOutcomesThisAnimal.empty:
        #     print("EMPTY!")

        tdiffs = []
        tempInDate = pd.to_datetime(dfThisIntakeThisAnimal.values[0][3])



        for outdatetime in dfOutcomesThisAnimal.outcome_datetime:
            tempOutDate = pd.to_datetime(outdatetime)
            tdiff = pd.Timedelta(tempOutDate - tempInDate)
            tdiffs.append(tdiff)

        testdiffs = [t for t in tdiffs if t >= pd.to_timedelta(0.0)]
        if dfOutcomesThisAnimal.empty:#len(tdiffs) == 0:#| dfOutcomesThisAnimal.empty
            print('[DATA]: matching outcome dates NOT found for {} this Intake Animal ID and Intake Date: {}'.format(dfThisIntakeThisAnimal['animal_id'].values,dfThisIntakeThisAnimal['datetime'].values))
            nullrow_cols = ['outcome_index', 'outcome_animal_id', 'outcome_name', 'outcome_datetime', 'outcome_monthyear','outcome_date_of_birth', 'outcome_type', 'outcome_subtype','outcome_animal_type', 'sex_upon_outcome', 'age_upon_outcome','outcome_breed', 'outcome_color']
            nullrow = pd.DataFrame(np.nan, index=[numiter], columns=nullrow_cols)
            #print(nullrow)
            #print(dfThisIntakeThisAnimal)
            # nullrow =
            newrow = np.concatenate((dfThisIntakeThisAnimal.values, nullrow.values), axis=None)
            inAndOutData.append(newrow)
        elif len(testdiffs) != 0:# & tempInDate < tempOutDate:
            print('yes! outcome date found...')
            m = np.min(testdiffs)
            match_index = tdiffs.index(m)
            this_index = 0

            # My biggest problem was that my enumerate function started at 1
            needsave = True
            for i, row in enumerate(dfOutcomesThisAnimal.values,1):
                if i-1 == match_index:
                    newrow = np.concatenate((dfThisIntakeThisAnimal.values, row), axis=None)
                    inAndOutData.append(newrow)
                    break
                else: # this is not the correct match
                    pass
        else:
            print('[DATA]: outcomes exist for this animal but no outcomes recorded after this intake date Animal ID: {} and Intake Date: {} and Outcome Dates: {}'.format(dfThisIntakeThisAnimal['animal_id'].values,dfThisIntakeThisAnimal['datetime'].values, dfOutcomesThisAnimal['outcome_datetime'].values))
            nullrow_cols = ['outcome_index', 'outcome_animal_id', 'outcome_name', 'outcome_datetime', 'outcome_monthyear','outcome_date_of_birth', 'outcome_type', 'outcome_subtype','outcome_animal_type', 'sex_upon_outcome', 'age_upon_outcome','outcome_breed', 'outcome_color']
            nullrow = pd.DataFrame(np.nan, index=[numiter], columns=nullrow_cols)
            #print(nullrow)
            #print(dfThisIntakeThisAnimal)
            # nullrow =
            newrow = np.concatenate((dfThisIntakeThisAnimal.values, nullrow.values), axis=None)
            inAndOutData.append(newrow)

        # Output data
        if numiter % 100 == 1:
            now_time = time.time()
            delta_time = now_time - start_time
            # print('[INFO]: time:{:10.2f} s  Match at{:7d}   Length of Stay:   {} days'.format(delta_time,index_animal_id, m.days))
            print('[INFO]: delta time:{:10.4f}    Match at{:10d}'.format(delta_time,index_animal_id))
        numiter+=1



    # # Combined Columns
    # combined_columns = ['unnamed:_0' 'animal_id' 'name' 'datetime' 'monthyear' 'found_location'
    #  'intake_type' 'intake_condition' 'animal_type' 'sex_upon_intake'
    #  'age_upon_intake' 'breed' 'color' 'outcome_unnamed:_0'
    #  'outcome_animal_id' 'outcome_name' 'outcome_datetime' 'outcome_monthyear'
    #  'outcome_date_of_birth' 'outcome_type' 'outcome_subtype'
    #  'outcome_animal_type' 'sex_upon_outcome' 'age_upon_outcome'
    #  'outcome_breed' 'outcome_color']

    # Outcome columns
    # ['outcome_unnamed:_0', 'outcome_animal_id', 'outcome_name', 'outcome_datetime', 'outcome_monthyear', 'outcome_date_of_birth', 'outcome_type', 'outcome_subtype', 'outcome_animal_type', 'sex_upon_outcome', 'age_upon_outcome', 'outcome_breed', 'outcome_color']

    outframe = pd.DataFrame(inAndOutData)
    outframe.columns = ['intake_index', 'animal_id', 'name', 'datetime', 'monthyear', 'found_location','intake_type', 'intake_condition', 'animal_type', 'sex_upon_intake','age_upon_intake', 'breed', 'color', 'outcome_index','outcome_animal_id', 'outcome_name', 'outcome_datetime', 'outcome_monthyear','outcome_date_of_birth', 'outcome_type', 'outcome_subtype','outcome_animal_type', 'sex_upon_outcome', 'age_upon_outcome','outcome_breed', 'outcome_color']
    outframe.to_csv('animalsAAC_{}.csv'.format(numiter), index=False)
