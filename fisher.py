import pandas as pd 
import numpy as np 
import yfinance as yahoo


### Agregar RSI, MACD, EWMA

class Strategy():
  
  def SimpleMovingAverage(symbol , num_days):
    """Provide financial 'symbol' to look data 
       Choose number of days for the metric"""
    data = pd.DataFrame(yahoo.download(symbol, period="1y")["Adj Close"].fillna(method="ffill"))
    data.columns = [i.replace('Adj Close',f'{symbol}') for i in data.columns] 
    bot = pd.DataFrame(data.values,columns=[f'{symbol}'],index=data.index)
    bot[f'SMA{num_days}'] = data[f'{symbol}'].rolling(round(num_days),min_periods=1).mean()
    bot['signal'] = 0.0
    bot['signal'] = np.where(bot[f'SMA{num_days}'] > data[f'{symbol}'], 1.0,0.0)
    bot['positions'] = bot['signal'].diff()
    return bot
    
  def Momentum(symbol, num_days):
    """Provide financial 'symbol' to look data 
       Choose number of days for the metric"""
    data = pd.DataFrame(yahoo.download(symbol, period="1y")["Adj Close"].fillna(method="ffill"))
    data.columns = [i.replace('Adj Close',f'{symbol}') for i in data.columns] 
    bot = pd.DataFrame(data.values,columns=[f'{symbol}'],index=data.index)
    bot['Momentum'] = data[f'{symbol}'] / data[f'{symbol}'].rolling(round(num_days),min_periods=1).mean()
    bot['signal'] = 0.0
    bot['signal'] = np.where(bot['Momentum'] < bot[f'{symbol}'], 1.0,0.0)
    bot['positions'] = bot['signal'].diff()
    return bot
    
  def BollingerBands(symbol, num_days,stdev_factor):
    """Provide financial 'symbol' to look data 
       Choose number of days for the metric
       number of factors for stdev to apply"""
    data = pd.DataFrame(yahoo.download(symbol, period="1y")["Adj Close"].fillna(method="ffill"))
    data.columns = [i.replace('Adj Close',f'{symbol}') for i in data.columns] 
    bot = pd.DataFrame(data.values,columns=[f'{symbol}'],index=data.index)
    bot['MiddleBand'] = bot[f'{symbol}'].rolling(round(num_days),min_periods=1).mean()
    bot['UpperBand'] = (bot['MiddleBand'] + int(stdev_factor) * bot[f'{symbol}'].rolling(round(num_days),min_periods=1).std())
    bot['LowerBand'] = (bot['MiddleBand'] - int(stdev_factor) * bot[f'{symbol}'].rolling(round(num_days),min_periods=1).std())
    return bot
  
  def StandardDeviation(symbol , num_days):
    """Provide financial 'symbol' to look data 
       Choose number of days for the metric"""
    data = pd.DataFrame(yahoo.download(symbol, period="1y")["Adj Close"].fillna(method="ffill"))
    data.columns = [i.replace('Adj Close',f'{symbol}') for i in data.columns] 
    bot = pd.DataFrame(data.values,columns=[f'{symbol}'],index=data.index)
    bot[f'StDev{num_days}'] = data[f'{symbol}'].rolling(round(num_days),min_periods=1).std()
    bot['signal'] = 0.0
    bot['signal'] = np.where(bot[f'StDev{num_days}'] > data[f'{symbol}'], 1.0,0.0)
    bot['positions'] = bot['signal'].diff()
    return bot
  

    
  