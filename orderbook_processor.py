import numpy as np
import time
from collections import deque

class OrderBookProcessor:
    def __init__(self, history_size=100):
        self.price_history = deque(maxlen=history_size)
        self.spread_history = deque(maxlen=history_size)
        self.timestamp_history = deque(maxlen=history_size)

    def update(self, orderbook: dict):
        try:
            bids = orderbook.get("bids", [])
            asks = orderbook.get("asks", [])
            ts = orderbook.get("timestamp", time.time())

            if not bids or not asks:
                return None

            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])
            mid_price = (best_bid + best_ask) / 2
            spread = best_ask - best_bid

            self.price_history.append(mid_price)
            self.spread_history.append(spread)
            self.timestamp_history.append(time.time())

            return {
                "mid_price": mid_price,
                "spread": spread,
                "volatility": self._compute_volatility(),
                "best_bid": best_bid,
                "best_ask": best_ask
            }
        except Exception as e:
            print(f"[OrderBookProcessor] Error: {e}")
            return None

    def _compute_volatility(self):
        if len(self.price_history) < 2:
            return 0.0
        returns = np.diff(self.price_history) / self.price_history[:-1]
        return np.std(returns) * 100  # percent

    def get_latest_metrics(self):
        if not self.price_history:
            return {}
        return {
            "mid_price": self.price_history[-1],
            "spread": self.spread_history[-1],
            "volatility": self._compute_volatility()
        }
