#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 


# In[2]:


import numpy as np


# In[3]:


import matplotlib.pyplot as plt


# In[4]:


import itertools


# In[5]:


from datetime import datetime


# In[6]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[7]:


from statsmodels.tsa.arima.model import ARIMA


# In[8]:


timeseries = pd.read_csv('crude-oil-exports-by-type-monthly.csv', header=0,delimiter=',')
timeseries = timeseries.loc[timeseries['Oil Type']=='Total'].filter(['Period','Volume (bbl/d)'])
timeseries['Period'] = timeseries['Period'].transform(lambda x: datetime.strptime(x, '%m/%d/%Y'))
timeseries.set_index(keys='Period', drop=True, inplace=True)
timeseries = timeseries.squeeze(axis=1)


# In[9]:


timeseries.plot()


# In[10]:


import warnings
warnings.filterwarnings("ignore")

p = range(0,10)
d = q = range(0,3)
pdq = list(itertools.product(p, d, q))
best_pdq = (0,0,0)
best_aic = np.inf
for params in pdq:
  model_test = ARIMA(timeseries, order = params)
  result_test = model_test.fit()
  if result_test.aic < best_aic:
    best_pdq = params
    best_aic = result_test.aic
print(best_pdq, best_aic)


# In[11]:


result_test.summary()


# In[12]:


result_test.plot_diagnostics(figsize=(15, 10))
plt.show()


# In[13]:


pred = result_test.get_prediction(start='2000-01-01', end='2023-01-01', dynamic=False)
pred_ci = pred.conf_int()

ax = timeseries['2000':].plot(label='observed', figsize=(20, 10))
pred.predicted_mean.plot(ax=ax, label='forecast', alpha=.7)
ax.fill_between(pred_ci.index,
pred_ci.iloc[:, 0],
pred_ci.iloc[:, 1], color='k', alpha=.2)
ax.set_xlabel('Дата')
ax.set_ylabel('Средний объем экспорта нефти (баррелей в день)')
plt.legend()
plt.show()


# In[ ]:




