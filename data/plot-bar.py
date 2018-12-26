import matplotlib
# matplotlib.use('Agg')

import numpy as np
import pandas as pd

import matplotlib.cm as cm
import matplotlib.pyplot as plt; plt.rcdefaults()
from mpld3 import fig_to_html, plugins
import time
import datetime

import os

def getdailyinventory( day, dataf ):
    dayinventory = dataf[(dataf.intake_date <= day) & (dataf.outcome_date > day)]
    return dayinventory

def dailyinventory( startdate, enddate, dataf ):
    date_format = "%Y-%m-%d"
    diff = datetime.strptime(enddate, date_format) - datetime.strptime(startdate, date_format)
    numdays = diff.days
    oneday = datetime.strptime("2015-01-02", date_format) - datetime.strptime("2015-01-01", date_format)
    days = [ (oneday * x + datetime.strptime(startdate, date_format) ) for x in range(numdays) ]
    print(days)
    #days = [ datetime.strptime(startdate, date_format) + oneday * day for day in numdays ]# list of days between start and enddates in ISODate format
    #print days
    #dayinventory = dataf[(dataf.intake_date <= day) & (dataf.outcome_date > day)]
    print( oneday, numdays)
    return #dayinventory

def getmonthlyintake( day1, day2, dataf):
    monthlyintake = dataf[(dataf.intake_date < day2) & (dataf.intake_date >= day1)]
    return len(monthlyintake)

def getmonthlyoutcome( day1, day2, dataf):
    monthlyinventory = dataf[(dataf.outcome_date < day2) & (dataf.outcome_date >= day1)]

# def barchart_counts( dataf , n ):
#     cnts = dataf[headers[n]].value_counts()[0:8]
#     keys = [ cnts.keys()[i] for i in range(0,len(cnts.keys())) ]
#     y_pos = np.arange(len(keys))
#     vals = cnts.values
#     plt.bar(y_pos, vals, align='center', alpha=0.5)
#     plt.xticks(y_pos, keys)
#     plt.ylabel('Counts')
#     plt.title(headers[n] + ' breakdown')
#     plt.show()
#     return plt 

def barchart_counts( dataf , n ):
    cnts = dataf[headers[n]].value_counts()[0:8]
    keys = [ cnts.keys()[i] for i in range(0,len(cnts.keys())) ]
    y_pos = np.arange(len(keys))
    vals = cnts.values
    fig = plt.figure(figsize=(12,6))
    plt.bar(y_pos, vals, align='center', alpha=0.5)
    plt.xticks(y_pos, keys)
    plt.ylabel('Counts')
    plt.title(headers[n] + ' breakdown')
    plt.grid()
    return fig

def filter_data( dataf ):
    # Process columns
    dataf.columns = [ col.lower() for col in dataf.columns]
    dataf.columns = [ col.replace(':','') for col in dataf.columns]
    dataf.columns = [ col.replace(' ','_') for col in dataf.columns]
    dataf.columns = [ col.replace('\n','') for col in dataf.columns]
    dataf.columns = [ col.replace('\t','') for col in dataf.columns]
    # dataf = dataf.rename(columns={ dataf.columns[0]: "index" })

    # Remove Dead Intake
    dataf = dataf[(dataf['intake_type']!="DEAD")&(dataf['intake_subtype']!="DEAD")&(dataf['intake_cond']!="DEAD")&(dataf['intake_type']!="DISPOSAL")&(dataf['intake_subtype']!="DISPOSAL")&(dataf['intake_cond']!="DISPOSAL")&(dataf['intake_type']!="DECEASED")&(dataf['intake_subtype']!="DECEASED")&(dataf['intake_cond']!="DECEASED")]
    # Remove Lost & Found group
    dataf = dataf[(dataf['intake_type']!="LOST&FOUND")&(dataf['intake_subtype']!="WEB")&(dataf['intake_cond']!="HOME EXP")]
    # Remove pre 2016 intake
    dataf = dataf[(pd.to_datetime(dataf.intake_date)<=pd.to_datetime("2018-12-31")) & (pd.to_datetime(dataf.outcome_date)>=pd.to_datetime("2017-01-01")) & (dataf['intake_cond']!="HOME EXP")]
    # Calculate New Fields LOS and Days Old
    dataf['los'] = (pd.to_datetime(dataf.outcome_date) - pd.to_datetime(dataf.intake_date))/ np.timedelta64(1, 'D')
    dataf['days_old'] = (pd.to_datetime(dataf.intake_date) - pd.to_datetime(dataf.dob))/ np.timedelta64(1, 'D')
    dataf['los_1'] = (pd.to_datetime(dataf.location_1_date) - pd.to_datetime(dataf.intake_date))/ np.timedelta64(1, 'D')
    dataf['los_2'] = (pd.to_datetime(dataf.location_2_date) - pd.to_datetime(dataf.location_1_date))/ np.timedelta64(1, 'D')
    dataf['age_s_n_date'] = (pd.to_datetime(dataf.s_n_date) - pd.to_datetime(dataf.dob))/ np.timedelta64(1, 'D')
    dataf['weight_difference'] = dataf.weight_1_week - dataf.weight
    dataf['in_to_due_out_date_diff'] = (pd.to_datetime(dataf.due_out_date) - pd.to_datetime(dataf.intake_date))/ np.timedelta64(1, 'D')
    dataf['due_out_to_outcome_date_diff'] = (pd.to_datetime(dataf.outcome_date) - pd.to_datetime(dataf.due_out_date))/ np.timedelta64(1, 'D')

    dataf['los_1'] = dataf['los_1'].round(5)
    dataf['los_2'] = dataf['los_2'].round(5)
    dataf['in_to_due_out_date_diff'] = dataf['in_to_due_out_date_diff'].round(5)
    dataf['due_out_to_outcome_date_diff'] = dataf['due_out_to_outcome_date_diff'].round(5)
    dataf['weight_difference'] = dataf['weight_difference'].round(3)
    # Change Animal Type field based on days old metric
    oldSpecs = dataf['animal_type']
    daysOld = dataf['days_old']
    newSpecs = []

    # Change Animal Type (a.k.a Species) field to reflect age as defined as less than
    #   or equal to 150 days old
    for i in range(len(dataf)):
        if pd.to_timedelta(daysOld.values[i]) <= pd.to_timedelta(150): 
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
    dataf['animal_type'] = newSpecs
    ### Drop values with intake dates in the future
    dataf = dataf[ ( pd.to_datetime(dataf['intake_date']) < pd.to_datetime('2018-12-31') ) ]
    # Process null columns
    # dataf = dataf.dropna(how='all', axis=1)
    # dataf = dataf.dropna(how='all', axis=0,inplace=True)
    # Save columns as seperate structure to return with the processed dataframe
    columns = dataf.columns
    return dataf, columns

print("[INFO]: Main thread is awake")
# Setup file paths to data
data_dir = './olddata/'
filename = 'animals.xls'
animals_dat = pd.read_excel( data_dir + filename )

dat, headers = filter_data(animals_dat)

print(dat.head())
print(dat.shape)
print(headers)

fig = barchart_counts(dat, 3)
plt.show()

from subprocess import call

writer = pd.ExcelWriter('./animals.xls')

if os.path.exists('./animals.tsv'):
    print('[INFO]: tsv File exists! ')
    dat.to_csv('./animals.tsv', sep='\t', index=False)
else:
    dat.to_csv('./animals.tsv', sep='\t', index=False)

if os.path.exists('./animals.csv'):
    print('[INFO]: csv File exists! ')
    dat.to_csv('./animals.csv', index=False)
else:
    dat.to_csv('./animals.csv', index=False)

if os.path.exists('./animals.xls'):
    print('[INFO]: xls File exists! ')
    dat.to_excel(writer,'Sheet1', index=False)
    writer.save()
else:
    dat.to_excel(writer,'Sheet1', index=False)
    writer.save()


# if __name__ == "__main__":
#     ''' Run code in main thread '''
#     print("[INFO]: Main thread is awake")
#     # Setup file paths to data
#     data_dir = '../data/'
#     filename = 'animals.csv'

#     animals_dat = pd.read_csv( data_dir + filename )
#     dat, headers = filter_data(animals_dat)

#     print(dat.head())
#     print(dat.shape)
#     print(headers)

#     plt = barchart_counts(dat, 3)
#     plt.show()