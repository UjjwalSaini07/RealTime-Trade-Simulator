import numpy as np
import joblib
from dataclasses import dataclass
from typing import Optional


@dataclass
class AlmgrenChrissParams:
    sigma: float  # volatility (annualized)
    eta: float    # temporary impact coefficient
    gamma: float  # permanent impact coefficient
    T: float      # total execution horizon (seconds or normalized time)
    X: float      # total shares (positive number: sell positive? it's convention)
    N: int        # number of slices


class AlmgrenChrissModel:

    def __init__(self, params: AlmgrenChrissParams):
        if params.N <= 0:
            raise ValueError("N must be > 0")
        self.params = params
        self.dt = self.params.T / self.params.N

    def optimal_trade_schedule(self) -> np.ndarray:
        """
        Returns:
            trade_sizes: numpy array of length N representing the shares to trade in each interval.
        """
        sigma = self.params.sigma
        eta = self.params.eta
        gamma = self.params.gamma
        T = self.params.T
        X = self.params.X
        N = self.params.N

        kappa = np.sqrt(gamma / eta) * sigma if eta > 0 and gamma > 0 else 0.0

        times = np.linspace(0, T, N)
        if kappa == 0.0:
            trade = np.full(N, X / N)
            return trade

        sinh_kappaT = np.sinh(kappa * T)
        x_t = X * (np.sinh(kappa * (T - times)) / sinh_kappaT)
        x_next = np.append(x_t[1:], 0.0)
        trade_sizes = x_t - x_next
        trade_sizes *= (X / max(1e-12, trade_sizes.sum()))
        return trade_sizes

    def expected_cost(self) -> float:
        """
        Compute an approximation of expected cost (implementation follows Almgren-Chriss formula).
        Returns:
            expected implementation shortfall (in same price unit as input parameters)
        """
        sigma = self.params.sigma
        eta = self.params.eta
        gamma = self.params.gamma
        X = self.params.X
        T = self.params.T
        N = self.params.N
        dt = self.dt

        trade_sizes = self.optimal_trade_schedule()
        # temporary impact cost component: sum(eta * (v_i^2) )
        temp_cost = eta * np.sum(trade_sizes ** 2)
        # permanent impact: gamma * X^2 / 2 (classic term)
        perm_cost = 0.5 * gamma * (X ** 2)
        # risk term approximated: sigma * sqrt(dt) * sum(|remaining inventory|)
        # approximate using L2 norm of inventory path
        inventory = np.cumsum(np.append(0.0, trade_sizes))[:-1]
        risk_cost = sigma * np.sqrt(dt) * np.sum(np.abs(inventory))

        return float(temp_cost + perm_cost + risk_cost)

    def save(self, path: str):
        joblib.dump(self.params, path)

    @staticmethod
    def load(path: str) -> AlmgrenChrissParams:
        return joblib.load(path)
