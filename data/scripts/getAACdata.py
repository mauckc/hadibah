# Python 3
# Get data from Austin Animal Care at data.austin texas.gov

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import os
import io
import requests

intakes_data_link = 'https://data.austintexas.gov/api/views/wter-evkm/rows.csv?accessType=DOWNLOAD'
outcomes_data_link = 'https://data.austintexas.gov/api/views/9t4d-g238/rows.csv?accessType=DOWNLOAD'
stray_map_data_link = 'https://data.austintexas.gov/api/views/kz4x-q9k5/rows.csv?accessType=DOWNLOAD'
download_data_links = (intakes_data_link, outcomes_data_link, stray_map_data_link)

print(download_data_links)

datadir = './'
intakes_data = 'Austin_Animal_Center_Intakes.csv'
outcomes_data = 'Austin_Animal_Center_Outcomes.csv'
stray_data = 'Austin_Animal_Center_Stray_Map.csv'
data_links = (datadir + intakes_data, datadir + outcomes_data, datadir + stray_data)

print(data_links)

def getAAC():
    content_l = [io.StringIO(requests.get(link).content.decode('utf-8')) for link in download_data_links ]
    # content_l =  [io.StringIO(s.decode('utf-8'))  for s in content_l ]
    for i, content in enumerate(content_l):
        df = pd.read_csv(content)
        df.to_csv(data_links[i])
        print('[INFO]: DONE!')

getAAC()

# if not os.path.exists('./Austin_Animal_Center_Intakes.csv'):
#     s = requests.get(intakes_data_link).content
#     dat_decoded = io.StringIO(s.decode('utf-8'))
#     df = pd.read_csv(io.StringIO(s.decode('utf-8')))
#     df.to_csv('Austin_Animal_Center_Intakes.csv')
#
# if not os.path.exists('./Austin_Animal_Center_Outcomes.csv'):
#     s = requests.get(outcomes_data_link).content
#     dat_decoded = io.StringIO(s.decode('utf-8'))
#     df = pd.read_csv(io.StringIO(s.decode('utf-8')))
#     df.to_csv('Austin_Animal_Center_Outcomes.csv')
#
# if not os.path.exists('./Austin_Animal_Center_Stray_Map.csv'):
#     s = requests.get(stray_map_data_link).content
#     dat_decoded = io.StringIO(s.decode('utf-8'))
#     df = pd.read_csv(io.StringIO(s.decode('utf-8')))
#     df.to_csv('Austin_Animal_Center_Stray_Map.csv')
