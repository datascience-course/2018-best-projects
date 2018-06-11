# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Data Science Final Project

import pandas as pd
import scipy as sc
import numpy as np

import matplotlib.pyplot as plt  
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (10, 6)

#%%

df = pd.read_csv('TOA5_1341Sonic20Hz_10.dat', skiprows=1, header=[0,1,2], low_memory=False)
df.head()
df.columns