#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 15:14:39 2018

@author: u1142223
"""

#%%  JUPYTER NOTEBOOK STARTS HERE

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
import scipy as sc
import numpy as np
import datetime as dt
import sys

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
#df_T1 = df1[['TIMESTAMP','T_Sonic_L','T_Sonic_M','T_Sonic_U']]
dfsonic = dfsonic[['TIMESTAMP','T_Sonic_L','T_Sonic_M','T_Sonic_U']]
dfsonic_bothT = dfsonic_bothT[['TIMESTAMP','T_Sonic_L','FW_L','T_Sonic_M','FW_M','T_Sonic_U','FW_U']]
dfspddir = dfspddir[['TIMESTAMP','L direction','L speed','M direction','M speed','U direction','U speed']]
dfspddir_bothT = dfspddir_bothT[['TIMESTAMP','L direction','L speed','M direction','M speed','U direction','U speed']]

print(dfsonic.head())
print(dfsonic_bothT.head())
print(dfspddir.head())
print(dfspddir_bothT.head())


#%% finding adjustment value for Tsonic

temp_cols = ['T_Sonic_L','FW_L','T_Sonic_M','FW_M','T_Sonic_U','FW_U']
dftest = dfsonic_bothT.dropna(axis=0, how='all', subset = temp_cols) #drop all rows that contain all NaNs


time = pd.date_range(start='2017-08-16', periods=dftest.shape[0], freq='1min')
plt.plot(time,dftest['T_Sonic_L'])
plt.plot(time,dftest['FW_L'])
plt.legend()
plt.show()

plt.plot(time,dftest['T_Sonic_M'])
plt.plot(time,dftest['FW_M'])
plt.legend()
plt.show()

plt.plot(time,dftest['T_Sonic_U'])
plt.plot(time,dftest['FW_U'])
plt.legend()
plt.show()

# based on plots above, deltas look constant
# will try calculating constant value, subtracting from T_Sonic
# and plotting results

#create table of deltas

dftest['diff_L'] = dftest['T_Sonic_L']-dftest['FW_L']
dftest['diff_M'] = dftest['T_Sonic_M']-dftest['FW_M']
dftest['diff_U'] = dftest['T_Sonic_U']-dftest['FW_U']

print(dftest['diff_L'].describe())
print(dftest['diff_M'].describe())
print(dftest['diff_U'].describe())

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
# adjust T_sonic_M and T_sonic_U in large dataframe where only T_sonic was available

#%% correct T_sonic_M and T_sonic_U

# visualized data before correction
plt.plot(dfsonic['T_Sonic_L']) #visualize
plt.plot(dfsonic['T_Sonic_M']) #visualize
plt.plot(dfsonic['T_Sonic_U']) #visualize
plt.legend()
plt.show()

#correct first half of data
N = int(dfsonic.shape[0]/2)
dfsonic['T_Sonic_M'][:N] = dfsonic['T_Sonic_M'][:N] - 12.4
dfsonic['T_Sonic_U'][:N] = dfsonic['T_Sonic_U'][:N] - 5.6

plt.plot(dfsonic['T_Sonic_L']) #visualize
plt.plot(dfsonic['T_Sonic_M']) #visualize
plt.plot(dfsonic['T_Sonic_U']) #visualize
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
df = pd.concat([dfsdcc, dftempcc[['T_Sonic_L', 'T_Sonic_M', 'T_Sonic_U']]], axis=1)
#df = df.drop(df.columns[7], axis=1)#drop 2nd TIMESTAMP column
print('Concatenated, complete dataframe shape: ',df.shape,'\n')
print(df.head())

df.describe()
plt.plot_date(x=df['TIMESTAMP'],y=df['U speed'])

#%% eliminate rows with all NaNs
temp_cols = df.columns[-9:]
dfclean = df.dropna(axis=0, how='any', subset = temp_cols) #drop all rows that contain any NaNs
dfclean = dfclean.reset_index()
del dfclean['index']
print('Concatenated, complete dataframe shape: ',dfclean.shape,'\n')
print('Percentage of data lost due to NaNs: ',(100-(dfclean.shape[0]/df.shape[0]*100)))
print(dfclean.head())

#%% plot data time-series

#plt.plot(dfclean['L direction'])
#plt.plot(dfclean['M direction'])
#plt.plot(dfclean['U direction'])
#plt.xlabel('Index')
#plt.ylabel('Wind Direction (degrees)')
#plt.legend()
#plt.show()
#
#plt.plot_date(x=dfclean['TIMESTAMP'],y=dfclean['U speed'])
#plt.plot_date(x=dfclean['TIMESTAMP'],y=dfclean['M speed'])
#plt.plot_date(x=dfclean['TIMESTAMP'],y=dfclean['L speed'])
#plt.xlabel('Time')
#plt.ylabel('Wind Speed (m/s)')
#plt.legend()
#plt.show()

plt.plot(dfclean['U speed'])
plt.plot(dfclean['M speed'])
plt.plot(dfclean['L speed']) #this might be best to use bc it's at the level of the solar panels and most conservative
plt.title('Sonic Data: Wind Speed')
plt.xlabel('Index')
plt.ylabel('Wind Speed (m/s)')
plt.legend()
plt.show()

plt.plot_date(x=dfclean['TIMESTAMP'],y=dfclean['T_Sonic_L'])
plt.plot_date(x=dfclean['TIMESTAMP'],y=dfclean['T_Sonic_M'])
plt.plot_date(x=dfclean['TIMESTAMP'],y=dfclean['T_Sonic_U'])
plt.title('Sonic Data: Adjusted Finewire Temperature')
plt.xlabel('Time')
plt.ylabel('Temperature (deg C)')
plt.legend()
plt.show()

plt.plot(dfclean['T_Sonic_L'])
plt.plot(dfclean['T_Sonic_M'])
plt.plot(dfclean['T_Sonic_U'])
plt.title('Sonic Data: Adjusted Finewire Temperature')
plt.xlabel('Index')
plt.ylabel('Temperature (deg C)')
plt.legend()
plt.show()

#%% save as csv for others
dfclean.to_csv('dfclean_sonicdata.csv')