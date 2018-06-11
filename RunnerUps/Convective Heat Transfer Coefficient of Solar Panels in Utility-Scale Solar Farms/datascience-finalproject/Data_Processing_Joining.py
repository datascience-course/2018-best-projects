#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 12:59:10 2018

@author: u1142223
"""

#%% Data Processing

# We have two datasets that require different levels of processing.  Many of the experimental variables were pre-processed and stored in a .csv file called "summerdata.csv" however the higher-quality data for temperature, wind speed, and wind direction was originally scattered across several folders and files.

# The code below first processes the sonic data and then combines it with the summerdata.csv to create a complete dataframe for analysis.

## Processing of the Sonic Data
#
#The sonic data was taken at 20Hz frequency from May 18 to August 19, 2017 and included several measurements such as Ux, Uy, Uz (wind speed and direction), Tsonic and FW (temperature), relative humidity, radiation.  In its raw form, this data is binary and not easily usable.  The data was first converted from its binary state into readable CSVs using the LoggerNet software associated with the Campbell Scientific dataloggers.  These CSVs were scattered among subfolders for each day of the experiment, totaling a size of 48 GB, with data that remained unusable.
#
#The data was then processed with "UTESpac," found at the link below, which reduced the data using 1-minute averages (to match the other experimental data frequency), re-oriented the measurements, and stored the data into a Matlab structure.
#https://github.com/derek591/UTESpac
#
#Due to minor differences in the measurement data taken, resulting in different numbers of columns among files, UTESpac was run twice for the two subsets of files with matching numbers of columns, resulting in two output Matlab structures.  UTESpac ran for a total of approximately 2.5 hours to process all files.  Since we only needed two variables from this structure, which contained our wind speed, wind direction, and temperature, Matlab's "csvwrite" function was used as shown below.  
#

#csvwrite('Sonic20Hz.csv',outputStruct.Sonic20Hz)
#csvwrite('spdAndDir.csv',outputStruct.spdAndDir)
#
#Four .csv files were generated for the two UTESpac outputs and concatenated using the code below.

#%%
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (10, 6)

#%%
# concatenate data into one usable spreadsheet

# "L" = lower sonic at 0.91m
# "M" = middle sonic at 1.829m
# "U" = upper sonic at 2.769m

# for "Sonic20Hz.csv" files
names = ['TIMESTAMP','Ux_0.91','Uy_0.91','Uz_0.91','T_Sonic_L','sonic_diag_0.91',
          'Ux_1.829','Uy_1.829','Uz_1.829','T_Sonic_M','sonic_diag_1.829',
          'Ux_2.769','Uy_2.769','Uz_2.769','T_Sonic_U','sonic_diag_2.769']

namesboth = ['TIMESTAMP','Ux_0.91','Uy_0.91','Uz_0.91','T_Sonic_L','sonic_diag_0.91','FW_L',
          'Ux_1.829','Uy_1.829','Uz_1.829','T_Sonic_M','sonic_diag_1.829','FW_M',
          'Ux_2.769','Uy_2.769','Uz_2.769','T_Sonic_U','sonic_diag_2.769','FW_U']

# for "spdAndDir.csv" files
names2 = ['TIMESTAMP','L direction','L speed','0.91m flag 295<dir<335',
          'M direction','M speed','1.829m flag 295<dir<335',	
          'U direction','U speed','2.769m flag 295<dir<335']

#load in csv for most of the data
dfsonic = pd.read_csv('sonic data/Sonic20Hz_1min.csv',header=None,names=names,index_col=False)
dflongtime = pd.read_csv('sonic data/longtime.csv',header=None,names=['TIME'],parse_dates=True,infer_datetime_format=True)
dflongtime['TIME'] = pd.to_datetime(dflongtime['TIME'],infer_datetime_format=True)
dfsonic['TIMESTAMP'] = dflongtime['TIME'] #replace TIMESTAMP column w/ date-time strings

#plt.plot(x=dfsonic['TIMESTAMP'],y=dfsonic['T_Sonic_L'])

dfspddir = pd.read_csv('sonic data/spdAndDir_1min.csv',header=None,names=names2,index_col=False)
dfspddir['TIMESTAMP'] = dflongtime[['TIME']] #replace TIMESTAMP column w/ date-time strings

#load in csv for last 4 days of the data
dfsonic_bothT = pd.read_csv('sonic data/Sonic20Hz_1min_bothT.csv',header=None,names=namesboth,index_col=False)
dfshorttime = pd.read_csv('sonic data/shorttime.csv',header=None,names=['TIME'],parse_dates=True)
dfshorttime['TIME'] = pd.to_datetime(dfshorttime['TIME'],infer_datetime_format=True)
dfsonic_bothT['TIMESTAMP'] = dfshorttime[['TIME']]

dfspddir_bothT = pd.read_csv('sonic data/spdAndDir_1min_bothT.csv',header=None,names=names2,index_col=False)
dfspddir_bothT['TIMESTAMP'] = dfshorttime[['TIME']]


#%% eliminate all unnecessary columns; keep only temperature columns
dfsonic = dfsonic[['TIMESTAMP','T_Sonic_L','T_Sonic_M','T_Sonic_U']]
dfsonic_bothT = dfsonic_bothT[['TIMESTAMP','T_Sonic_L','FW_L','T_Sonic_M','FW_M','T_Sonic_U','FW_U']]
dfspddir = dfspddir[['TIMESTAMP','L direction','L speed','M direction','M speed','U direction','U speed']]
dfspddir_bothT = dfspddir_bothT[['TIMESTAMP','L direction','L speed','M direction','M speed','U direction','U speed']]

print('dfsonic:\n')
print(dfsonic.head())
print('\n dfsonic_both:\n')
print(dfsonic_bothT.head())
print('\n dfspddir:\n')
print(dfspddir.head())
print('\n dfspddir_both:\n')
print(dfspddir_bothT.head())


#%% 
## Adjustment of Temperature Variable within Sonic Data
# 
# For the first half of the experiment, temperature was measured by the sonics themselves in a variable called "T_sonic."  This method of measuring temperature can be inaccurate.  For the second half of the experiment, temperature was measured by finewire sensors in a variable called "FW."  This method of measuring temperature is accurate.  During the last 4 days of the experiment, temperature was measured by both methods, adding another column to that subset of the data. The difference between T_sonic and FW is quantified using the last 4 days of the experiment when both measurement methods were present.  

# The following code finds this adjustment value, adjusts T_sonic during the first half of the summer, and combines all the sonic data into a single dataset.

#%% finding adjustment value for Tsonic

temp_cols = ['T_Sonic_L','FW_L','T_Sonic_M','FW_M','T_Sonic_U','FW_U']
dftest = dfsonic_bothT.dropna(axis=0, how='all', subset = temp_cols) #drop all rows that contain all NaNs

time = pd.date_range(start='2017-08-16', periods=dftest.shape[0], freq='1min') #create time vector for visualization purposes only

plt.plot(time,dftest['T_Sonic_L'])
plt.plot(time,dftest['FW_L'])
plt.title('Comparing T_Sonic to FW for Lower Sonic')
plt.xlabel('Time')
plt.ylabel('Temperature (deg C)')
plt.legend()
plt.show()

plt.plot(time,dftest['T_Sonic_M'])
plt.plot(time,dftest['FW_M'])
plt.title('Comparing T_Sonic to FW for Middle Sonic')
plt.xlabel('Time')
plt.ylabel('Temperature (deg C)')
plt.legend()
plt.show()

plt.plot(time,dftest['T_Sonic_U'])
plt.plot(time,dftest['FW_U'])
plt.title('Comparing T_Sonic to FW for Upper Sonic')
plt.xlabel('Time')
plt.ylabel('Temperature (deg C)')
plt.legend()
plt.show()

# based on plots above, deltas look constant
# will try calculating constant value, subtracting from T_Sonic
# and plotting results

#add columns of deltas to existing df
dftest['diff_L'] = dftest['T_Sonic_L']-dftest['FW_L']
dftest['diff_M'] = dftest['T_Sonic_M']-dftest['FW_M']
dftest['diff_U'] = dftest['T_Sonic_U']-dftest['FW_U']

print('Difference between T_sonic and FW for Lower Sonic')
print(dftest['diff_L'].describe(),'\n')
print('Difference between T_sonic and FW for Middle Sonic')
print(dftest['diff_M'].describe(),'\n')
print('Difference between T_sonic and FW for Upper Sonic')
print(dftest['diff_U'].describe(),'\n')

#Interpretation:
# On the lower sonic, because the mean and max temperature difference between 
# the two measuremnts T_sonic and Finewire were so small (<1 deg C), no adjustment
# is needed.
#
# On the middle sonic, the mean temperatue difference is 12.4 deg C and standard
# deviation was 0.2 deg C, so an adjustment value of 12.4 deg C was chosen.
#
# On the upper sonic, the mean temperatue difference is 5.6 deg C and standard
# deviation was 0.2 deg C, so an adjustment value of 5.6 deg C was chosen.
#
#

#%% adjust T_sonic_M and T_sonic_U

# visualize data before correction
plt.plot(dfsonic['T_Sonic_L']) #visualize
plt.plot(dfsonic['T_Sonic_M']) #visualize
plt.plot(dfsonic['T_Sonic_U']) #visualize
plt.title('Temperature data before adjustment')
plt.xlabel('Index')
plt.ylabel('Temperature (deg C)')
plt.legend()
plt.show()

#correct first half of data
N = int(dfsonic.shape[0]/2)
dfsonic['T_Sonic_M'][:N] = dfsonic['T_Sonic_M'][:N] - 12.4
dfsonic['T_Sonic_U'][:N] = dfsonic['T_Sonic_U'][:N] - 5.6

plt.plot(dfsonic['T_Sonic_L']) #visualize
plt.plot(dfsonic['T_Sonic_M']) #visualize
plt.plot(dfsonic['T_Sonic_U']) #visualize
plt.title('Temperature data after adjustment')
plt.xlabel('Index')
plt.ylabel('Temperature (deg C)')
plt.legend()
plt.show()


#%% swap contents of T_Sonic and FW columns because we are going to disregard T_sonic and replace everything with an adjusted temperature
dfsonic_bothT[['T_Sonic_L', 'FW_L']] = dfsonic_bothT[['FW_L', 'T_Sonic_L']]
dfsonic_bothT[['T_Sonic_M', 'FW_M']] = dfsonic_bothT[['FW_M', 'T_Sonic_M']]
dfsonic_bothT[['T_Sonic_U', 'FW_U']] = dfsonic_bothT[['FW_U', 'T_Sonic_U']]

dfsoniclast = dfsonic_bothT[['TIMESTAMP','T_Sonic_L','T_Sonic_M','T_Sonic_U']] #get rid of inaccurate measurements now called 'FW'

#%% concatenate sonic data

#concatenate vertically
dftempcc = pd.concat([dfsonic, dfsoniclast], ignore_index=True)
print('Concatenated temperature dataframe shape: ',dftempcc.shape)

dfsdcc = pd.concat([dfspddir, dfspddir_bothT], ignore_index=True)
print('Concatenated spd+dir dataframe shape: ',dftempcc.shape)

#concatenate horizontally
#df = pd.concat([dfsdcc, dftempcc], axis=1, verify_integrity=True)  #verify that TIMESTAMP col is same: it is
#df = pd.merge(left=dfsdcc, right=dftempcc, how='left', on='TIMESTAMP')
dfson = pd.concat([dfsdcc, dftempcc[['T_Sonic_L', 'T_Sonic_M', 'T_Sonic_U']]], axis=1)
#df = df.drop(df.columns[7], axis=1)#drop 2nd TIMESTAMP column
print('Concatenated, complete dataframe shape: ',dfson.shape,'\n')
print(dfson.head())
print('\n Dataframe Info: \n',dfson.describe())

#%% plots: visualize processed sonic data
plt.plot_date(x=dfson['TIMESTAMP'],y=dfson['U speed'])
plt.title('Timeseries plot of processed sonic data')
plt.xlabel('Time')
plt.ylabel('Wind Velocity (m/s)')
plt.legend()
plt.show()

plt.plot(dfson['U speed'])
plt.title('Index plot of processed sonic data')
plt.xlabel('Index')
plt.ylabel('Wind Velocity (m/s)')
plt.legend()
plt.show()

plt.plot_date(x=dfson['TIMESTAMP'],y=dfson['T_Sonic_L'])
plt.title('Timeseries plot of processed sonic data')
plt.xlabel('Time')
plt.ylabel('Temperature (deg C))')
plt.legend()
plt.show()

# %%

## Processing and Joining with "summerdata.csv"
#
# The following code joins the two datasets wherever TIMESTAMP exists in both datasets.

#%%
data = pd.read_csv('summerdata.csv')
data = data.rename(columns={"Time":"TIMESTAMP"})

#%% 

#convert TIMESTAMP column to datetime type
dfsummertime = pd.read_csv('summertimestamp.csv',header=None,names=['TIME'],parse_dates=True,infer_datetime_format=True)
dfsummertime['TIME'] = pd.to_datetime(dfsummertime['TIME'],infer_datetime_format=True)
data['TIMESTAMP'] = dfsummertime['TIME'] #replace TIMESTAMP column w/ date-time strings
data2017 = data[(data['TIMESTAMP']>'2017-01-01')] #only select data from 2017
#data2017['TIMESTAMP'] = pd.to_datetime(data2017['TIMESTAMP'],infer_datetime_format=True)
#data2017 = data2017.reset_index()

print('summerdata:')
print(data2017.head())
#print('ensure TIMESTAMP column is correct datetime data type: \n',data2017['TIMESTAMP'].describe())


#%% plot summerdata

#plt.plot_date(x=data2017['TIMESTAMP'],y=data2017['h'])
#plt.plot(data2017['h'],'.') 
#plt.plot(data2017['CupWS_ms'])

#data2017['TIMESTAMP'].describe()
#dfsdcc['TIMESTAMP'].describe()

#%% merge data2017 with dfson

#dfson['TIMESTAMP']=dfson['TIMESTAMP'].replace(second=0, microsecond=0)
#data2017['TIMESTAMP'].replace(second=0, microsecond=0)
#data2017['TIMESTAMP']=data2017['TIMESTAMP'].strftime('%Y-%m-%d %H:%M')

# ensure both 'TIMESTAMP' columns are in matching format
#data2017['TIMESTAMP'] = data2017['TIMESTAMP'].apply(lambda dt: dt.replace(second=0, microsecond=0))
data2017['TIMESTAMP'] = data2017['TIMESTAMP'].apply(lambda dt: dt.strftime('%Y-%m-%d %H:%M'))

#dfson['TIMESTAMP'] = dfson['TIMESTAMP'].apply(lambda dt: dt.replace(second=0, microsecond=0))
dfson['TIMESTAMP'] = dfson['TIMESTAMP'].apply(lambda dt: dt.strftime('%Y-%m-%d %H:%M'))

#intersection = np.intersect1d(dfson['TIMESTAMP'], data2017['TIMESTAMP'])
#difference = np.setdiff1d(dfson['TIMESTAMP'], data2017['TIMESTAMP'])

#dfjoined = df.join(data2017, on='TIMESTAMP',how='outer',lsuffix='_left')
#dfjoined = pd.merge(data2017, df, how='inner', on=['TIMESTAMP'])

dfjoined = data2017.set_index('TIMESTAMP').join(dfson.set_index('TIMESTAMP')) #join the two datasets
print('joined dataset shape:',dfjoined.shape)
print('Joined DF created by joining df of shape:',dfson.shape,'and data2017 of shape:',data2017.shape)
print('# rows in common:',dfjoined.shape[0],' out of: ',dfson.shape[0])
print('Joined DF:',dfjoined.head())

      
#%% save as csv for others
dfjoined.to_csv('dfjoined.csv') #includes NaN rows

#intersection has different size than dfjoined has rows?
 
#%% eliminate unnecessary columns: 'BattV', 'Btemp1',
#       'Btemp2', 'Btemp3', 'Btemp4', 'Btemp5', 'Btemp6', 'TempBmid', 'Btemp14',
#       'Btemp15', 'Btemp16', 'TempB', 'Btemp22', 'Btemp23', 'TempTmid',
#       'TempT', 'FinewireT_Top', 'FinewireT_Mid', 'FinewireT_Bot',

      # removing FW temperature and local solar panel temperatures from summerdata.csv
cols = ['ApogSWup', 'ApogSWdn', 'ApogLWup', 'ApogLWdn', 'CNR_SWup', 'CNR_SWdn',
       'CNR_LWup', 'CNR_LWdn', 'HMP_TempC', 'HMP_RH', 'CupWS_ms', 'CupWD', 'CupWD_SD', 'q', 'h', 'L direction', 'L speed',
       'M direction', 'M speed', 'U direction', 'U speed', 'T_Sonic_L',
       'T_Sonic_M', 'T_Sonic_U']
dftrunc = dfjoined[cols]

#%% eliminate rows with all NaNs
temp_cols = dftrunc.columns
df = dftrunc.dropna(axis=0, how='any', subset = temp_cols) #drop all rows that contain any NaNs
#df = df.reset_index()
#del dfclean['index']
print('Concatenated, complete dataframe shape: ',df.shape,'\n')
print('Percentage of data lost due to NaNs: ',(100-(df.shape[0]/dftrunc.shape[0]*100)))
print(df.head())

#%%
# Exploratory Analysis of Complete Dataset
#
# The following code visually explores the data available to us in the complete dataset.


# plots

plt.plot(df['U speed'])
plt.plot(df['M speed'])
plt.plot(df['L speed']) #this might be best to use bc it's at the level of the solar panels and most conservative
plt.title('Wind Speed at 3 Sonic Heights')
plt.xlabel('Index')
plt.autofmt_xdate()
plt.ylabel('Wind Speed (m/s)')
plt.legend()
plt.show()

plt.plot_date(x=df['TIMESTAMP'],y=df['T_Sonic_L'])
plt.plot_date(x=df['TIMESTAMP'],y=df['T_Sonic_M'])
plt.plot_date(x=df['TIMESTAMP'],y=df['T_Sonic_U'])
plt.title('Time-series plot of temperature at 3 sonic heights')
plt.xlabel('Time')
plt.ylabel('Temperature (deg C)')
plt.legend()
plt.show()

plt.plot(df['T_Sonic_L'])
plt.plot(df['T_Sonic_M'])
plt.plot(df['T_Sonic_U'])
plt.title('Temperature at 3 sonic heights')
plt.xlabel('Index')
plt.ylabel('Temperature (deg C)')
plt.legend()
plt.show()

plt.plot(df['h'])
plt.title('Heat transfer coefficient: h (from energy balance)')
plt.xlabel('Index')
plt.ylabel('Wind Speed (m/s)')
plt.legend()
plt.show()

#%% save as csv for others
df.to_csv('dfcomplete.csv')

