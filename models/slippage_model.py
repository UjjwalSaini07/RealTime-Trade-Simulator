import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

class SlippageModel:
    """
    Regression-based slippage prediction model.
    """
    def __init__(self, degree=1):
        self.degree = degree
        self.model = None
        if degree > 1:
            self.poly = PolynomialFeatures(degree)
        else:
            self.poly = None

    def fit(self, X: pd.DataFrame, y: pd.Series):
        if self.degree > 1:
            X_poly = self.poly.fit_transform(X)
            self.model = LinearRegression().fit(X_poly, y)
        else:
            self.model = LinearRegression().fit(X, y)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.degree > 1 and self.poly:
            X_poly = self.poly.transform(X)
            return self.model.predict(X_poly)
        else:
            return self.model.predict(X)
