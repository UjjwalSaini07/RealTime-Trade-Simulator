import pandas as pd
from sklearn.linear_model import LogisticRegression

class MakerTakerModel:
    """
    Logistic regression model to predict maker/taker order classification.
    """
    def __init__(self):
        self.model = LogisticRegression()

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """
        Train the logistic regression model.

        Args:
            X: feature DataFrame
            y: binary target Series (1=maker, 0=taker)
        """
        self.model.fit(X, y)

    def predict_proba(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Returns:
            DataFrame with columns ['maker_prob', 'taker_prob']
        """
        probs = self.model.predict_proba(X)
        return pd.DataFrame(probs, columns=['taker_prob', 'maker_prob'])

    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Returns:
            Series of 0/1 indicating taker/maker.
        """
        return pd.Series(self.model.predict(X))
