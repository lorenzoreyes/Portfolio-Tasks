Portfolio Tasks
This is my personal approach to handle portfolios's data cycles.
From getting the data, give proper format, take basic calculations and statistics,
to get an optimized portfolio 
NOTE = optimization taken reference from https://github.com/Stuj79 
and 
https://www.pythonforfinance.net/2019/07/02/investment-portfolio-optimisation-with-python-revisited/#more-16744
in this case i just optimize and adapt it to the portfolio I was working on

What you can do this with this?
From portfolio ultimate.py
(1) Request data of the portfolio you are gonna work with.
(2) Get returns of your assets.
(3) Get statistics and correlation info of your portfolio.
(4) Make your final portfolio, according to your first assign
of assets weigths do be hand.

From Portfolio optimize by monte carlo and sharpe.py
You can also do this to check your previous work
(5) Get the data and set the variables of your investment policy 
(i. e. what are your upper and lower bounds, if you short or use 
leverage and test the optimal weigths of your assets).
(6) Once you have your data and variables, you gonna calculate
your portfolio returns annualized, standard deviation and sharpe
ratio. 
(7) With previous data, you are going to run simulations in 
Monte Carlo, gonna run all previos data and variables creating
the specified number of portfolios. And you ask for max sharpe ratio
and min variance portfolios from the distribution you get.
(8) The Scipy.Optimize is the same process, but without simulations.
You calculate based on your historical data and apply all calculations
to look the empirical portfolios. 
