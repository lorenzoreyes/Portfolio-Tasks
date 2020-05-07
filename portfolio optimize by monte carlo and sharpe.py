
# import needed packages
import pandas as pd
import numpy as np
from pandas_datareader import data
import datetime as dt
import scipy.optimize as sco
from scipy import stats
import matplotlib.pyplot as plt

# request and format the needed data
tickers = ['IUSG', 'VLUE', 'IEV', 'EUDG', 'DEM', 'PICB', 'BNDX', 'IHY', 'CEMB',
          'SHY', 'PFE', 'MSFT', 'AMD', 'MCD', 'AAPL', 'AMZN', 'JPM', 'BA', 'KO']
start = dt.datetime(2016, 1, 1)
end = dt.datetime.today()
df = pd.DataFrame([data.DataReader(ticker, 'yahoo', start, end)['Adj Close'] for ticker in tickers]).T # request and get only Adj Close
df.columns = tickers # gets your tickers as columns
noa = len(df.columns)
weigths = np.random.random(noa)
weigths /= np.sum(weigths)
days = 252
alpha = 0.05
mean_returns = df.pct_change().mean()
cov = df.pct_change().cov()
num_portfolios = 100000
rf = 0.0
# Im using lower and upper bounds of -0.3 and 0.3, change it at your own need


# taste your data, get statistics and performance
# Do it by Monte Carlo Approach
# get performance returns, standard deviation and sharpe ratio
def calc_portfolio_perf(weights, mean_returns, cov, rf):
    portfolio_return = np.sum(mean_returns * weights) * 252
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights))) * np.sqrt(252)
    sharpe_ratio = (portfolio_return - rf) / portfolio_std
    return portfolio_return, portfolio_std, sharpe_ratio

# run simulations of your portfolio
def simulate_random_portfolios(num_portfolios, mean_returns, cov, rf):
    results_matrix = np.zeros((len(mean_returns) + 3, num_portfolios))
    for i in range(num_portfolios):
        weights = np.random.random(len(mean_returns))
        weights /= np.sum(weights)
        portfolio_return, portfolio_std, sharpe_ratio = calc_portfolio_perf(weights, mean_returns, cov, rf)
        results_matrix[0, i] = portfolio_return
        results_matrix[1, i] = portfolio_std
        results_matrix[2, i] = sharpe_ratio
        # iterate through the weight vector and add data to results array (return, std and sharpe)
        for j in range(len(weights)):
            results_matrix[j + 3, i] = weights[j]
    results_df = pd.DataFrame(results_matrix.T, columns=['ret', 'stdev', 'sharpe'] + [ticker for ticker in tickers])
    return results_df

results_frame = simulate_random_portfolios(num_portfolios, mean_returns, cov, rf)

max_sharpe_port = results_frame.iloc[results_frame['sharpe'].idxmax()]

min_vol_port = results_frame.iloc[results_frame['stdev'].idxmin()]

# Do it by Scipy Optimization minimize function
def calc_neg_sharpe(weights, mean_returns, cov, rf):
    portfolio_return = np.sum(mean_returns * weights) * 252
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights))) * np.sqrt(252)
    sharpe_ratio = (portfolio_return - rf) / portfolio_std
    return -sharpe_ratio

constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

def max_sharpe_ratio(mean_returns, cov, rf):
    num_assets = len(mean_returns)
    args = (mean_returns, cov, rf)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = (-0.3,0.3)
    bounds = tuple(bound for asset in range(num_assets))
    result = sco.minimize(calc_neg_sharpe, num_assets*[1./num_assets,], args=args,
                        method='SLSQP', bounds=bounds, constraints=constraints)
    return result

optimal_port_sharpe = max_sharpe_ratio(mean_returns, cov, rf)

optimal_sharpe = pd.DataFrame([round(x,4) for x in optimal_port_sharpe['x']],index=tickers)

def calc_portfolio_std(weights, mean_returns, cov):
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights))) * np.sqrt(252)
    return portfolio_std

def min_variance(mean_returns, cov):
    num_assets = len(mean_returns)
    args = (mean_returns, cov)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = (-0.3,0.3)
    bounds = tuple(bound for asset in range(num_assets))
    result = sco.minimize(calc_portfolio_std, num_assets*[1./num_assets,], args=args,
                        method='SLSQP', bounds=bounds, constraints=constraints)
    return result

min_port_variance = min_variance(mean_returns, cov)

minimal = pd.DataFrame([round(x,2) for x in min_port_variance['x']],index=tickers)


writer = pd.ExcelWriter('portfolio optimized100.xlsx', engine='xlsxwriter')

df.to_excel(writer,sheet_name='basic data')

results_frame.to_excel(writer, sheet_name='simulations')

max_sharpe_port.to_excel(writer, sheet_name='maximum sharpe')

min_vol_port.to_excel(writer, sheet_name='minimal volatility portfolio')

optimal_sharpe.to_excel(writer, sheet_name='optimal sharpe scipy')

minimal.to_excel(writer, sheet_name='minimal variance by scipy')

writer.save()