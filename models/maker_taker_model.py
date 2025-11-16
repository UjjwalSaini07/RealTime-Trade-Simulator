import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from typing import Optional

class MakerTakerModel:
    def __init__(self, model: Optional[Pipeline] = None):
        # default pipeline: standard scaler + logistic regression
        self.model = model or Pipeline(
            [("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=200))]
        )

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """
        Train the logistic regression model.

        Args:
            X: feature DataFrame
            y: binary target Series (1=maker, 0=taker)
        """
        if X is None or y is None or len(X) == 0:
            raise ValueError("Empty X or y passed to fit()")
        self.model.fit(X, y)

    def predict_proba(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Returns:
            DataFrame with columns ['maker_prob', 'taker_prob']
        """
        probs = self.model.predict_proba(X)
        classes = list(self.model.named_steps["clf"].classes_)
        try:
            idx_maker = classes.index(1)
            idx_taker = classes.index(0)
        except ValueError:
            idx_taker, idx_maker = 0, 1 if probs.shape[1] > 1 else (0, 0)
        maker_prob = probs[:, idx_maker]
        taker_prob = probs[:, idx_taker]
        return pd.DataFrame({"maker_prob": maker_prob, "taker_prob": taker_prob})

    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Returns:
            Series of 0/1 indicating taker(0)/maker(1).
        """
        preds = self.model.predict(X)
        return pd.Series(preds, name="maker_flag")

    def save(self, path: str):
        """Persist model to disk (joblib)."""
        joblib.dump(self.model, path)

    def load(self, path: str):
        """Load model from disk (joblib)."""
        self.model = joblib.load(path)
