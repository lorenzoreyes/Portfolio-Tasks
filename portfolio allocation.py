import yfinance as yahoo
import pandas as pd
import numpy as np
import scipy.optimize as sco
from scipy import stats
import matplotlib.pyplot as plt


stocks = ['X','BBD','NOK','WFC','ERJ','VALE','HMY','AIG','GE','ABEV',
         'PBR','INTC','KO','RTX','TOT','GILD','PFE','AZN',
          'NVDA','JNJ','NFLX','DIS','TGT','MSFT','AMZN','AAPL','GOOGL', 'WMT']

df = yahoo.download(stocks,period="1y",interval="60m")['Adj Close'].fillna(method='ffill')
noa = len(df.columns)
weigths = np.random.random(noa)
weigths /= np.sum(weigths)
observations = len(df.index)
mean_returns = df.pct_change().mean()
cov = df.pct_change().cov()
alpha = 0.05
rf = 0.0


def calc_neg_sharpe(weights, mean_returns, cov, rf):
    portfolio_return = np.sum(mean_returns * weights) * observations
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights))) * np.sqrt(observations)
    sharpe_ratio = (portfolio_return - rf) / portfolio_std
    return -sharpe_ratio

constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

def max_sharpe_ratio(mean_returns, cov, rf):
    num_assets = len(mean_returns)
    args = (mean_returns, cov, rf)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = (0.0,0.125)
    bounds = tuple(bound for asset in range(num_assets))
    result = sco.minimize(calc_neg_sharpe, num_assets*[1./num_assets,], args=args,
                        method='SLSQP', bounds=bounds, constraints=constraints)
    return result

optimal_port_sharpe = max_sharpe_ratio(mean_returns, cov, rf)

optimo = pd.DataFrame(index=df.columns)
optimo['weights'] = optimal_sharpe = pd.DataFrame([round(x,4) for x in optimal_port_sharpe['x']],index=df.columns)
optimo = optimo.sort_values('weights',axis=0,ascending=False)

def calc_portfolio_VaR(weights, mean_returns, cov, alpha, observations):
    portfolio_return = np.sum(mean_returns * weights) * observations
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights))) * np.sqrt(observations)
    portfolio_var = abs(portfolio_return - (portfolio_std * stats.norm.ppf(1 - alpha)))
    return portfolio_var

def min_VaR(mean_returns, cov, alpha, observations):
    num_assets = len(mean_returns)
    args = (mean_returns, cov, alpha, observations)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = (0.0,0.3)
    bounds = tuple(bound for asset in range(num_assets))
    result = sco.minimize(calc_portfolio_VaR, num_assets*[1./num_assets,], args=args,
                        method='SLSQP', bounds=bounds, constraints=constraints)
    return result

min_port_VaR = min_VaR(mean_returns, cov, alpha, observations)

minimal_VaR = pd.DataFrame(index=df.columns)
minimal_VaR['weights'] = pd.DataFrame([round(x,4) for x in min_port_VaR['x']],index=df.columns)

minimal_VaR = minimal_VaR.sort_values('weights',axis=0,ascending=False)


portfoliosharpe = (df * optimo.weights).T.sum()

portfoliominimal = (df * minimal_VaR.weights).T.sum()

benchmark = df.T.mean() # build an equally weigthed portfolio to use as benchmark

assets_return = df.pct_change().cumsum() # spectrum of the assets returns


sharpe = pd.DataFrame(index=df.columns)
sharpe['weigths'] = pd.DataFrame([round(x,2) for x in optimal_port_sharpe['x']],index=df.columns)
sharpe.weigths.sort_values(axis=0,ascending=False)

data = df

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

portfolio = data.T.mean()

portfolio_returns = (portfolio - portfolio.shift(1))/ portfolio.shift(1)

portfolio_stats = portfolio_returns.describe(percentiles=[.01,.05,.10]).T

portfolio_stats['var'] = portfolio_returns.var()

portfolio_stats['skew'] = portfolio_returns.skew()

portfolio_stats['Kurtosis'] = portfolio_returns.kurtosis()

risk = pd.DataFrame(index=data.columns)
risk['numerator'] = (instruments.deltas.multiply(covariance)).sum()
risk['denominator'] = portfolio_returns.std() * (-2.32635) # at 1% of inverse normal dist.
risk['GradVaR'] = -risk.numerator / risk.denominator
risk['CVaRj'] = risk.GradVaR * instruments.deltas # Component VaR of the Risk Factors j
risk['thetai'] = (risk.CVaRj * correlation).sum() # Theta i of the instruments
risk['CVaRi'] = risk.thetai * (1/len(data.columns)) # Component VaR of the Instruments i
risk['totalCVaRi'] = risk.CVaRi.sum() #total CVaR of the portfolio
risk['CVaRattribution'] = risk.CVaRi / risk.totalCVaRi # risk allocation by instrument in the portfolio

cartera = pd.DataFrame(index=data.columns)
cartera['base'] = instruments.weigths
cartera['CVaRattribution'] = risk.CVaRattribution.sort_values(axis=0,ascending=False)
cartera['new'] = minimal_VaR.weights
cartera['condition'] = (cartera.base  * cartera.CVaRattribution)
cartera['newrisk'] = (cartera.new  * cartera.CVaRattribution)
cartera['differences'] = (cartera.newrisk - cartera.condition)  # apply this result as a percentage to multiply new weights
cartera['adjustments'] = (cartera.newrisk - cartera.condition) / cartera.condition #ALARM if its negative sum up the difference, 
                                            #if it is positive rest it, you need to have 0
cartera['suggested'] = cartera.new * (1 + cartera.adjustments)   
cartera['tototal'] = cartera.suggested.sum()
cartera['MinCVaR'] = cartera.suggested / cartera.tototal


portfoliocvar = cartera.MinCVaR

carteras = pd.DataFrame(index=df.index)
carteras['sharpe'] = portfoliosharpe
carteras['minvar'] = portfoliominimal
carteras['cvar'] = portfoliocvar
carteras['benchmark'] = benchmark

stocks = ['X','BBD','NOKA','WFC','ERJ','VALE','HMY','AIG','GE','ABEV',
         'PBR','INTC','KO','RTX','TOT','GILD','PFE','AZN',
          'NVDA','JNJ','NFLX','DISN','TGT','MSFT','AMZN','AAPL','GOOGL','WMT']

string = '.BA'
BA = [x + string for x in stocks]
cedears = yahoo.download(BA,period="1d")['Adj Close']

# Cartera por Mínimo VaR
minvarport = pd.DataFrame(index=cedears.columns)
minvarport['capital'] = float(100000) # en miles
minvarport['precio'] = cedears.T
minvarport['weights'] = (minimal_VaR['weights'].values).round(2)
minvarport['efectivo'] = (minvarport['capital'] * minvarport['weights'])
minvarport['fracción'] =  minvarport['efectivo'] / minvarport['precio'] 
minvarport['redondo'] = minvarport['fracción'].round()
minvarport['invertido'] = minvarport['precio'] * minvarport['redondo']
minvarport['porcentage'] = minvarport['invertido'] / sum(minvarport['invertido'])
minvarport['total'] = sum(minvarport['invertido'])

# Cartera Max Sharpe
sharport = pd.DataFrame(index=cedears.columns)
sharport['capital'] = float(100000) # en miles
sharport['precio'] = cedears.T
sharport['weights'] = (optimo.weights.values).round(2)
sharport['efectivo'] = (sharport['capital'] * sharport['weights'])
sharport['fracción'] =  sharport['efectivo'] / sharport['precio'] 
sharport['redondo'] = sharport['fracción'].round()
sharport['invertido'] = sharport['precio'] * sharport['redondo']
sharport['porcentage'] = sharport['invertido'] / sum(sharport['invertido'])
sharport['total'] = sum(sharport['invertido'])

# Cartera CVaR
cvarport = pd.DataFrame(index=cedears.columns)
cvarport['capital'] = float(100000) # en miles
cvarport['precio'] = cedears.T
cvarport['weights'] = (cartera.MinCVaR.values).round(2)
cvarport['efectivo'] = (cvarport['capital'] * cvarport['weights'])
cvarport['fracción'] =  cvarport['efectivo'] / cvarport['precio'] 
cvarport['redondo'] = cvarport['fracción'].round()
cvarport['invertido'] = cvarport['precio'] * cvarport['redondo']
cvarport['porcentage'] = cvarport['invertido'] / sum(cvarport['invertido'])
cvarport['total'] = sum(cvarport['invertido'])

writer = pd.ExcelWriter('carteras primitivas.xlsx', engine='xlsxwriter')

minvarport.to_excel(writer, sheet_name='cartera minVaR')

sharport.to_excel(writer, sheet_name='cartera sharpe')

cvarport.to_excel(writer, sheet_name='cartera riesgo CVaR')

carteras.to_excel(writer, sheet_name='evolución cada cartera', index=False)

df.to_excel(writer, sheet_name='series tiempo activos', index=False)

returns.to_excel(writer, sheet_name='retorno activos', index=False)

statistics.to_excel(writer, sheet_name='estadisticos')

correlation.to_excel(writer, sheet_name='correlaciones')

covariance.to_excel(writer, sheet_name='covarianza')

instruments.to_excel(writer, sheet_name='datos riesgo instrumentos')

risk.to_excel(writer, sheet_name='medidas de riesgo')

cartera.to_excel(writer, sheet_name='optimizo por mincvar')

writer.save()




