""" a portfolio with a risky and a safe asset (Problem 3)

Starting point for the exam. The methods raising NotImplementedError are the ones
you should write yourself.

"""

from types import SimpleNamespace
import numpy as np

class PortfolioModelClass:
    """ a portfolio of a risky and a safe asset with a rebalancing rule """

    def __init__(self,**kwargs):
        """ set the default parameters, then overwrite with any keyword arguments """

        par = self.par = SimpleNamespace()

        # a. returns
        par.mu = 0.05 # mean log return on the risky asset
        par.sigma = 0.20 # standard deviation of the log return on the risky asset
        par.r = 0.01 # log return on the safe asset

        # b. the rebalancing rule
        par.theta_star = 0.50 # target share of wealth in the risky asset
        par.Delta = 0.10 # width of the no-trade band
        par.tau = 0.01 # proportional transaction cost

        # c. preferences
        par.gamma = 3.0 # relative risk aversion

        # d. simulation settings
        par.W0 = 1.0 # initial wealth
        par.T = 40 # number of periods
        par.N = 50_000 # number of simulated portfolios
        par.seed = 2026 # seed for the random number generator

        # e. overwrite with keyword arguments, e.g. PortfolioModelClass(Delta=0.0)
        for key,value in kwargs.items(): setattr(par,key,value)

        # f. empty container for simulation results
        self.sim = SimpleNamespace()

    def __str__(self):
        """ called when using print """

        par = self.par

        text = 'Portfolio model with:\n'
        text += f'  mu    = {par.mu:.4f}, sigma = {par.sigma:.4f}, r = {par.r:.4f}\n'
        text += f'  theta_star = {par.theta_star:.4f}, Delta = {par.Delta:.4f}, tau = {par.tau:.4f}\n'
        text += f'  gamma = {par.gamma:.4f} (relative risk aversion)\n'
        text += f'  W0 = {par.W0:.2f}, T = {par.T}, N = {par.N:,}, seed = {par.seed}'

        return text

    def draw_returns(self):
        """ draw the gross return on the risky asset in all periods and all portfolios

        Returns:

            (ndarray): gross returns with shape (N,T)

        """

        par = self.par

        rng = np.random.default_rng(par.seed)
        eps = rng.normal(size=(par.N,par.T))

        return np.exp(par.mu + par.sigma*eps)

    def u(self,W):
        """ CRRA utility of wealth """

        par = self.par

        return W**(1-par.gamma)/(1-par.gamma)

    # the share of wealth in the risky asset after trading, and the amount traded
    def trade(self,theta):
        """ apply the no-trade band rule to the risky share

        Args:
          theta (ndarray): pre-trade risky share at the start of a period, shape (N,)

        Returns:
           theta_post (ndarray): risky share after trading, shape (N,)
            amount (ndarray): size of the change in the risky share, |theta_post-theta|
            trade_now (ndarray of bool): True where a trade actually took place

        """

        par = self.par

        # a. restrictions by the no trade band
        trade_now = np.abs(theta - par.theta_star) > par.Delta

        # b. share after trading
        theta_post = np.where(trade_now,par.theta_star,theta)

        # c. amount traded
        amount = np.abs(theta_post - theta)

        return theta_post, amount, trade_now

    # simulate all N portfolios forward T periods
    def simulate(self,R=None):
        """ simulate all N portfolios forward T periods

        Loops over the T periods and vectorizes over the N portfolios. Pass R in
        to reuse the same drawn returns across several rules.

        Args:
        R (ndarray, optional): gross risky returns, shape (N,T). Drawn if None.

        """

        par = self.par
        sim = self.sim

        # a. draw the return if not supplied
        if R is None: R = self.draw_returns()
        Rf = np.exp(par.r) 

        # b. storing the values in the array of size (N,T)
        W = np.zeros((par.N,par.T+1))
        theta = np.zeros((par.N,par.T+1))
        traded = np.zeros((par.N,par.T),dtype=bool) 
        dist = np.zeros((par.N,par.T)) 

        # c. specifying the initial values
        W[:,0] = par.W0
        theta[:,0] = par.theta_star

        # d. looping through the periods with the vectorized portfolio
        for t in range(par.T):

            # i. initial distance to the target
            dist[:,t] = np.abs(theta[:,t] - par.theta_star)

            # ii. trade decision 
            theta_post, amount, trade_now = self.trade(theta[:,t])
            traded[:,t] = trade_now

            # iii. wealth after paying tau
            W_post = W[:,t]*(1 - par.tau*amount)

            # iv. realized returns
            W[:,t+1] = theta_post*W_post*R[:,t] + (1-theta_post)*W_post*Rf

            # v. risky share in the next period
            theta[:,t+1] = theta_post*W_post*R[:,t]/W[:,t+1]

        # e. storing the results
        sim.R = R
        sim.W = W
        sim.theta = theta
        sim.traded = traded
        sim.dist = dist
        sim.WT = W[:,-1] # terminal wealth

    # the numbers to report for a rule, including expected utility
    def summary(self):
        """ the six numbers to report for the current rule

        Returns:
        (SimpleNamespace): n_trades, avg_dist, mean_WT, median_WT, p10_WT, EU

        """

        par = self.par
        sim = self.sim

        res = SimpleNamespace()

        # a. average number of trades over the T periods
        res.n_trades = sim.traded.sum(axis=1).mean()

        # b. average distance to the target
        res.avg_dist = sim.dist.mean()

        # c. terminal wealth statistics
        WT = sim.WT
        res.mean_WT = WT.mean()
        res.median_WT = np.median(WT)
        res.p10_WT = np.percentile(WT,10)

        # 6. expected utility
        res.EU = self.u(WT).mean()

        return res
