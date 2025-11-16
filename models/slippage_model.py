import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from typing import Optional
import joblib

class SlippageModel:

    def __init__(self, degree: int = 1):
        self.degree = int(degree)
        steps = []
        if self.degree > 1:
            steps.append(("poly", PolynomialFeatures(self.degree, include_bias=False)))
        steps.append(("reg", LinearRegression()))
        self.pipeline = Pipeline(steps)

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """
        Fit the model.

        X: features (DataFrame or 2D array-like)
        y: target slippage (Series or 1D array)
        """
        if X is None or y is None or len(X) == 0:
            raise ValueError("Empty X or y passed to fit()")
        self.pipeline.fit(X, y)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict slippage values for given features.

        Returns numpy array of predicted slippages.
        """
        return self.pipeline.predict(X)

    def save(self, path: str):
        joblib.dump({"degree": self.degree, "pipeline": self.pipeline}, path)

    def load(self, path: str):
        obj = joblib.load(path)
        self.degree = obj.get("degree", 1)
        self.pipeline = obj["pipeline"]
