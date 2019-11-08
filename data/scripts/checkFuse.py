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
    intake_data_path = "Austin_Animal_Center_Intakes.csv"
    outcome_data_path = "Austin_Animal_Center_Outcomes.csv"
    inAndOutData_path = "allJoinedProcessedDataAAC.csv"

    dfintake = pd.read_csv(intake_data_path)
    headers_intake = list(dfintake.columns.values)
    print(headers_intake)
    print( np.shape(dfintake) )


    dfoutcome = pd.read_csv(outcome_data_path)
    headers_outcome = list(dfoutcome.columns.values)
    print(headers_outcome)
    print( np.shape(dfoutcome) )

    dfinAndOut = pd.read_csv(inAndOut_data_path)
    headers_inAndOut = list(dfinAndOut.columns.values)
    print(headersinAndOut)
    print( np.shape(dfinAndOut) )

    # Count how many times animal IDs show up in the other dataset
    intake_counter = 0
    for animal_id in dfintake['Animal ID']:
        if animal_id in dfinAndOut['animal_id']:
            intake_counter += 1

    print("[INFO]: Intake Counter: {}".format(intake_counter) )
    print("[INFO]: Total Intake: {}".format(dfintake.shape) )

    # Count how many times animal IDs show up in the other dataset
    outcome_counter = 0
    for animal_id in dfoutcome['Animal ID']:
        if animal_id in dfinAndOut['animal_id']:
            outcome_counter += 1

    print("[INFO]: Outcome Counter: {}".format(outcome_counter) )
    print("[INFO]: Total Outcomes: {}".format(dfoutcome.shape) )


    # dfinAndOut['los'] = [ pd.to_datetime(row['datetime']) -  pd.to_datetime(row['outcome_datetime']) for row in dfinAndOut ]
    dfinAndOut['los'] = pd.to_datetime(dfinAndOut['datetime']) -  pd.to_datetime(dfinAndOut['outcome_datetime'])

    los_value_counts = dfinAndOut['los'].value_counts()
    print(los_value_counts)
