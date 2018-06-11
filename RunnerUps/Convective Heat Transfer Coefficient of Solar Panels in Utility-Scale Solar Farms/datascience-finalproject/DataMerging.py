#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 14:43:29 2018

@author: u1142223
"""

#%%
import pandas as pd
import scipy as sc
import numpy as np
import datetime as dt
import sys

import matplotlib.pyplot as plt
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (10, 6)

data = pd.read_csv('summerdata.csv')
data = data.rename(columns={"Time":"TIMESTAMP"})

dfsummertime = pd.read_csv('summertimestamp.csv',header=None,names=['TIME'],parse_dates=True,infer_datetime_format=True)
dfsummertime['TIME'] = pd.to_datetime(dfsummertime['TIME'],infer_datetime_format=True)
data['TIMESTAMP'] = dfsummertime['TIME'] #replace TIMESTAMP column w/ date-time strings
data2017 = data[(data['TIMESTAMP']>'2017-01-01')] #only select data from 2017
#data2017['TIMESTAMP'] = pd.to_datetime(data2017['TIMESTAMP'],infer_datetime_format=True)
#data2017 = data2017.reset_index()
data2017.head()

#plt.plot_date(x=data2017['TIMESTAMP'],y=data2017['h'])
#plt.plot(data2017['h'],'.') ############################## remove outliers later or scale data
#plt.plot(data2017['CupWS_ms'])

data2017['TIMESTAMP'].describe()
#dfsdcc['TIMESTAMP'].describe()

#%% merge data2017 with df

#df['TIMESTAMP']=df['TIMESTAMP'].replace(second=0, microsecond=0)
#data2017['TIMESTAMP'].replace(second=0, microsecond=0)
#data2017['TIMESTAMP']=data2017['TIMESTAMP'].strftime('%Y-%m-%d %H:%M')

#data2017['TIMESTAMP'] = data2017['TIMESTAMP'].apply(lambda dt: dt.replace(second=0, microsecond=0))
data2017['TIMESTAMP'] = data2017['TIMESTAMP'].apply(lambda dt: dt.strftime('%Y-%m-%d %H:%M'))

#df['TIMESTAMP'] = df['TIMESTAMP'].apply(lambda dt: dt.replace(second=0, microsecond=0))
df['TIMESTAMP'] = df['TIMESTAMP'].apply(lambda dt: dt.strftime('%Y-%m-%d %H:%M'))

intersection = np.intersect1d(df['TIMESTAMP'], data2017['TIMESTAMP'])
difference = np.setdiff1d(df['TIMESTAMP'], data2017['TIMESTAMP'])

#dfjoined = df.join(data2017, on='TIMESTAMP',how='outer',lsuffix='_left')
#dfjoined = pd.merge(data2017, df, how='inner', on=['TIMESTAMP'])

dfjoined = data2017.set_index('TIMESTAMP').join(df.set_index('TIMESTAMP'))
print('# rows in common:',dfjoined.shape[0],' out of: ',df.shape[0])
      
#%% save as csv for others
dfjoined.to_csv('dfjoined.csv')

#intersection has different size than dfjoined has rows?
 
#%% eliminate unnecessary columns; keep only temperature columns

      # removing FW temperature and local solar panel temperatures from summerdata.csv
cols = ['ApogSWup', 'ApogSWdn', 'ApogLWup', 'ApogLWdn', 'CNR_SWup', 'CNR_SWdn',
       'CNR_LWup', 'CNR_LWdn', 'HMP_TempC', 'HMP_RH', 'CupWS_ms', 'CupWD', 'CupWD_SD', 'q', 'h', 'L direction', 'L speed',
       'M direction', 'M speed', 'U direction', 'U speed', 'T_Sonic_L',
       'T_Sonic_M', 'T_Sonic_U']
dftrunc = dfjoined[cols]     

#%% eliminate rows with all NaNs
temp_cols = dftrunc.columns
dfcomplete = dftrunc.dropna(axis=0, how='any', subset = temp_cols) #drop all rows that contain any NaNs
#dfcomplete = dfcomplete.reset_index()
#del dfclean['index']
print('Concatenated, complete dataframe shape: ',dfcomplete.shape,'\n')
print('Percentage of data lost due to NaNs: ',(100-(dfcomplete.shape[0]/dftrunc.shape[0]*100)))
print(dfcomplete.head())

#%% plots

plt.plot(dfcomplete['U speed'])
plt.plot(dfcomplete['M speed'])
plt.plot(dfcomplete['L speed']) #this might be best to use bc it's at the level of the solar panels and most conservative
plt.title('Sonic Data: Wind Speed')
plt.xlabel('Index')
plt.ylabel('Wind Speed (m/s)')
plt.legend()
plt.show()

plt.plot_date(x=dfcomplete['TIMESTAMP'],y=dfcomplete['T_Sonic_L'])
plt.plot_date(x=dfcomplete['TIMESTAMP'],y=dfcomplete['T_Sonic_M'])
plt.plot_date(x=dfcomplete['TIMESTAMP'],y=dfcomplete['T_Sonic_U'])
plt.title('Sonic Data: Adjusted Finewire Temperature')
plt.xlabel('Time')
plt.ylabel('Temperature (deg C)')
plt.legend()
plt.show()

plt.plot(dfcomplete['T_Sonic_L'])
plt.plot(dfcomplete['T_Sonic_M'])
plt.plot(dfcomplete['T_Sonic_U'])
plt.title('Sonic Data: Adjusted Finewire Temperature')
plt.xlabel('Index')
plt.ylabel('Temperature (deg C)')
plt.legend()
plt.show()

plt.plot(dfcomplete['h'])
plt.title('Complete data: h')
plt.xlabel('Index')
plt.ylabel('Wind Speed (m/s)')
plt.legend()
plt.show()

#%% save as csv for others
dfcomplete.to_csv('dfcomplete.csv')