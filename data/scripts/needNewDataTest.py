# Shelter data frame python pandas
# Python 2.7 file for processing csv files of animal intake reports
# File being read: "UCDavis_KE_5- 1-1-2012-5-31-2018.xls"
from datetime import datetime
import numpy as np
import time
import pandas as pd
#import matplotlib.pyplot as plt
import math
import os

path = './'
files = []
files = [i for i in os.listdir(path) if os.path.isfile(os.path.join(path,i)) and \
         'animalsAAC' in i]

if __name__ == '__main__':
    # Read csv to file using pandas
    # inAndOutData_path = "allJoinedProcessedDataAAC.csv"
    inAndOutData_path = "safe_noheaders_allJoinedProcessedDataAAC.csv"

    df = pd.read_csv(inAndOutData_path)

    headers_inAndOut = list(df.columns.values)
    print(headers_inAndOut)
    print( np.shape(df) )
    print(df.head())

    for file in files:
        print(file)

    # df.to_csv('animalsAAC_{}.csv'.format(datetime.now().strftime('%Y-%m-%d_%H_%M_%S')), index=False)
