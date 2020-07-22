import pandas as pd
import yfinance as yahoo

# Download Data of your instruments
stocks = ['IUSG', 'VLUE', 'IEV', 'EUDG', 'DEM', 'PICB', 'BNDX', 'IHY', 'CEMB',
          'SHY', 'PFE', 'MSFT', 'AMD', 'MCD', 'AAPL', 'AMZN', 'JPM', 'BA', 'KO']


data = yahoo.download(stocks, period="5y")['Adj Close']

data = data.fillna(method='ffill')

# Calculate the returns of instruments, statistics & correlation
returns = (data - data.shift(1))/ data.shift(1)# get the returns for every serie

statistics = returns.describe().T

statistics['mad'] = returns.mad()

statistics['skew'] = returns.skew()

statistics['kurtosis'] = returns.kurtosis()

statistics = statistics.T

correlation = returns.corr() # correlation

covariance = returns.cov()  # covariance

# Calculate the deltas of the instruments as the weights assigned multiplied by their correlations (elasticity)
instruments = pd.DataFrame(index= data.columns)
instruments['weigths'] = 1/len(instruments.index) # secure allocation is equal 1
instruments['deltas'] = (instruments.weigths * correlation).sum() # deltas as elasticity of the assets
instruments['Stdev'] = returns.std()
instruments['stress'] = (instruments.deltas * instruments.Stdev) * 3 # stress applied at 4 deviations
instruments['portfolio_stress'] = instruments.stress.sum() # the stress of the portfolio

# Optional, if all the worst events happen at once, must detect the worst deviation of the instruments and apply it simultaneously
poe = (returns / returns.std()).min()
fullstress = sum(instruments.stress.multiply(poe))

# Equally weigthed portfolio assumed to do the test unbiased
portfolio = ((data.IUSG * 0.0526) + (data.VLUE * 0.0526) + (data.IEV * 0.0526) + (data.EUDG * 0.0526) + (data.DEM * 0.0526) +
             (data.PICB	* 0.0526) + (data.BNDX * 0.0526) + (data.IHY * 0.0526) + (data.CEMB * 0.0526) + (data.SHY * 0.0526)
             + (data.PFE * 0.0526) + (data.MSFT * 0.0526) + (data.AMD * 0.0526) + (data.MCD * 0.0526) +(data.AAPL * 0.0526)
             + (data.AMZN * 0.0526) + (data.JPM * 0.0526) + (data.BA * 0.0526) + (data.KO * 0.0526))

# Calculate metrics of returns and statistics
portfolio_returns = (portfolio - portfolio.shift(1))/ portfolio.shift(1)

portfolio_stats = portfolio_returns.describe(percentiles=[.01,.05,.10]).T

portfolio_stats['var'] = portfolio_returns.var()

portfolio_stats['skew'] = portfolio_returns.skew()

portfolio_stats['Kurtosis'] = portfolio_returns.kurtosis()

#Calculate Gradients of VaR, as (deltas X covariance) divided by (Portfolio Std X 1% Inverse Cummulative dist.)
risk = pd.DataFrame(index=data.columns)
risk['numerator'] = (instruments.deltas.multiply(covariance)).sum()
risk['denominator'] = portfolio_returns.std() * (-2.32635) # at 1% of inverse normal dist.
risk['GradVaR'] = -risk.numerator / risk.denominator
risk['CVaRj'] = risk.GradVaR * instruments.deltas # Component VaR of the Risk Factors j
risk['thetai'] = (risk.CVaRj * correlation).sum() # Theta i of the instruments
risk['CVaRi'] = risk.thetai * (1/len(data.columns)) # Component VaR of the Instruments i
risk['totalCVaRi'] = risk.CVaRi.sum() #total CVaR of the portfolio
risk['CVaRattribution'] = risk.CVaRi / risk.totalCVaRi # risk allocation by instrument in the portfolio

writer = pd.ExcelWriter('portfolio risk.xlsx', engine='xlsxwriter')

data.to_excel(writer, sheet_name='dataseries')

returns.to_excel(writer, sheet_name='returns')

statistics.to_excel(writer, sheet_name='statistics')

correlation.to_excel(writer, sheet_name='correlation')

covariance.to_excel(writer, sheet_name='covariance')

portfolio.to_excel(writer, sheet_name='portfolioseries')

portfolio_returns.to_excel(writer, sheet_name='portfolioreturns')

portfolio_stats.to_excel(writer, sheet_name='portfoliostats')

instruments.to_excel(writer, sheet_name='instrumentsinfo')

risk.to_excel(writer, sheet_name='riskmetrics')

writer.save()




