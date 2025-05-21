import numpy as np

class AlmgrenChrissModel:
    """
    Almgren-Chriss optimal execution model for market impact estimation.
    """

    def __init__(self, sigma, eta, gamma, T, X, N):
        self.sigma = sigma
        self.eta = eta
        self.gamma = gamma
        self.T = T
        self.X = X
        self.N = N
        self.dt = T / N

    def optimal_trade_schedule(self):
        kappa = np.sqrt(self.gamma / self.eta) * self.sigma
        sinh_kappaT = np.sinh(kappa * self.T)
        times = np.linspace(0, self.T, self.N)

        x = self.X * (np.sinh(kappa * (self.T - times)) / sinh_kappaT)
        trade_sizes = -np.diff(np.append(x, 0))  # amount traded in each interval

        return trade_sizes

    def expected_cost(self):
        pass
