#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 07:22:52 2019

@author: mu
"""

import numpy as np
import pandas as pd
from pandas import Series, DataFrame 

class Stock():
    def __init__(self,stock):
        self.price=stock.copy()
        self.logprice=stock.copy()
        self.logprice.loc[:,'a':]=np.log(self.price.loc[:,'a':])
    def clean(self):
        """replace 0,1 by the forward fill
        """
        self.price.replace(np.nan,-1)
        self.price[(self.price.loc[:,'a':]==0 )|(self.price.loc[:,'a':]==1)]=np.nan
        self.price=self.price.fillna(method='ffill')
        self.price.replace(-1,np.nan)
        self.logprice.loc[:,'a':]=np.log(self.price.loc[:,'a':])
    def deepclean(self,stok,level=3,transaction=60):
        self.price.replace(np.nan,-1)
        for stk in stok:
        # select a timewindow depending on the trading frequency
            trade_factor=1/(np.nanmean(self.price.loc[:,stk].diff()!=0)+10**-7)
            timewindow=int(transaction*trade_factor)
       
            s=self.logprice.loc[:,stk]
        # standard deviation is adjusted by trade_factor
            leftmean,leftstd=s.rolling(timewindow).mean(),s.rolling(timewindow).std()*level*np.sqrt(trade_factor)
        # large variance could be coused by precidteable future events such as stock split, so check future variance as well
            self.price.loc[:,stk][(np.abs(self.logprice.loc[:,stk]-leftmean.shift(1))>leftstd.shift(1))&( np.abs(self.logprice.loc[:,stk]-leftmean.shift(-timewindow))>leftstd.shift(-timewindow))]=np.nan
            self.price=self.price.fillna(method='ffill')
            self.logprice.loc[:,stk]=np.log(self.price.loc[:,stk])
        self.price.replace(-1,np.nan)
    def split_adjust(self,stk):
        split_time=0
        while self.price[stk][split_time+1]>0.75*self.price[stk][split_time]:
            split_time+=1
        self.price[stk][:split_time+1]/=2
    def logrtn(self,stk,start,end,timespan=1):
        """ timespan<=390,unit=min"""
        return self.logprice[stk][start:end].diff(periods=timespan)
    def vol(self,stk,start,end,samplegap=1,timespan=390):
        if timespan%samplegap:
            print("timespan shall be divisible by samplegap")
            return np.nan
        frequency=int(timespan/samplegap)
        return np.nanstd(self.logprice[stk][start:end:samplegap][:(end-start)//timespan*frequency].values.reshape(-1,frequency),axis=1)*np.sqrt(252)
    def rlz_vol(self,stk,start,end,samplegap=1,timespan=390):
        """timespan shall be divisible by frequency,timespan is the span of volatility, can be daily(=390),hourly(=60),etc
        the unit is annualized volatility
        """
        if timespan%samplegap:
            print("timespan shall be divisible by samplegap")
            return np.nan
        frequency=int(timespan/samplegap)
        return np.sqrt(np.nanmean(np.square(self.logprice[stk][start:end:samplegap].diff()[:(end-start)//timespan*frequency]).values.reshape(-1,frequency),axis=1)*frequency*252)
    def abs_logrtn(self,stk,start,end,samplegap=1,timespan=390):
        """ 
        timespan can be hourly(=60), daily(=390),etc
        the unit is annualized volatility
        """
        if timespan%samplegap:
            print('timespan should be divisible by samplegap')
            return np.nan
        fre=int(timespan/samplegap)
        return np.nanmean(np.abs(self.logprice[stk][start:end:samplegap].diff()[:(end-start)//timespan*fre]).values.reshape(-1,fre),axis=1)*np.sqrt(fre*252)
    def monthly_vol(self,stk,start,end,samplegap=1):
        """
        unit: annualized volatility
        """
        if 390%samplegap:
            print('timespan should be divisible by samplegap')
            return np.nan
        fre=int(390/samplegap)
        return np.array(self.logprice[stk][start:end:samplegap].rolling(21*fre).std())[::fre]*np.sqrt(12)
        
        
            
    def monthly_absrtn(self,stk,start,end,samplegap=1):
        return self.abs_logrtn(stk,start,end,samplegap).rolling(21).mean()
        
    
        
                
        