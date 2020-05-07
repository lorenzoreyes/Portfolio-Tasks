import pandas as pd
import pandas_datareader as data
import datetime as dt


stocks = ['IUSG', 'VLUE', 'IEV', 'EUDG', 'DEM', 'PICB', 'BNDX', 'IHY', 'CEMB',
          'SHY', 'PFE', 'MSFT', 'AMD', 'MCD', 'AAPL', 'AMZN', 'JPM', 'BA', 'KO']

start = dt.datetime(2016,1,1)#'2016-01-01'

end = dt.date.today() #'2020-04-17'

df = data.DataReader(stocks, 'yahoo', start, end)['Adj Close']


data = pd.DataFrame(data=df) # Transform  into Pandas DataFrame

returns = (data - data.shift(1))/ data.shift(1)# get the returns for every serie

statistics = returns.describe().T

statistics['mad'] = returns.mad()

statistics['skew'] = returns.skew()

statistics['kurtosis'] = returns.kurtosis()

statistics = statistics.T

correlation = returns.corr() # correlation

# get your portfolio as the sum of every asset by their weight  CAMBIAR DATA PORT RETURNS ASI NO HACES PORTFOLIO RETURNS
portfolio = ((data.IUSG * 0.01) + (data.VLUE * 0.01) + (data.IEV * 0.01) + (data.EUDG * 0.01) + (data.DEM * 0.05) +
             (data.PICB	* 0.015) + (data.BNDX * 0.015) + (data.IHY * 0.08) + (data.CEMB * 0.07) + (data.SHY * 0.35)
             + (data.PFE * 0.05) + (data.MSFT * 0.05) + (data.AMD * 0.05) + (data.MCD * 0.05) +(data.AAPL * 0.05)
             + (data.AMZN * 0.05) + (data.JPM * 0.02) + (data.BA * 0.05) + (data.KO * 0.05))

portfolio_returns = (portfolio - portfolio.shift(1))/ portfolio.shift(1)

portfolio_stats = portfolio_returns.describe().T

portfolio_stats['mad'] = portfolio_returns.mad()

portfolio_stats['skew'] = portfolio_returns.skew()

portfolio_stats['Kurtosis'] = portfolio_returns.kurtosis()

writer = pd.ExcelWriter('ultimax aprils.xlsx', engine='xlsxwriter')

data.to_excel(writer, sheet_name='raw adj close series')

returns.to_excel(writer, sheet_name='returns')

statistics.to_excel(writer, sheet_name='statistics')

correlation.to_excel(writer, sheet_name='correlation')

portfolio.to_excel(writer, sheet_name='portfolio raw')

portfolio_returns.to_excel(writer, sheet_name='portfolio returns')

portfolio_stats.to_excel(writer, sheet_name='portfolio stats')

writer.save()

