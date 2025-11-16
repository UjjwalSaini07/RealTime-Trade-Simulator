from typing import Dict, List, Tuple, Any
import pandas as pd
import math

def process_orderbook_snapshot(snapshot: dict, top_n: int = 5) -> Dict[str, Any]:
    """
    Convert a raw orderbook snapshot (asks/bids lists) into a normalized dict
    with top_n levels, mid_price, spread, total volumes and a depth-weighted avg price.

    Expected snapshot format:
      { "asks": [[price_str, size_str], ...], "bids": [[price_str, size_str], ...], ... }

    Returns a dict with:
      - best_bid, best_ask, spread, mid_price
      - bids: list of (price: float, size: float) up to top_n
      - asks: list of (price: float, size: float) up to top_n
      - total_bid_volume, total_ask_volume
      - bid_dwa (depth-weighted avg price), ask_dwa
    """
    asks_raw = snapshot.get("asks") or []
    bids_raw = snapshot.get("bids") or []

    def _to_tuples(arr: List[List[Any]]) -> List[Tuple[float, float]]:
        out = []
        for p_sz in arr[:top_n]:
            try:
                p = float(p_sz[0])
                s = float(p_sz[1])
                if math.isfinite(p) and math.isfinite(s):
                    out.append((p, s))
            except Exception:
                continue
        return out

    asks = _to_tuples(asks_raw)
    bids = _to_tuples(bids_raw)

    if not asks or not bids:
        return {}

    best_ask = asks[0][0]
    best_bid = bids[0][0]
    spread = best_ask - best_bid
    mid_price = (best_ask + best_bid) / 2.0

    total_ask_volume = sum(sz for _, sz in asks)
    total_bid_volume = sum(sz for _, sz in bids)

    def depth_weighted_avg(items: List[Tuple[float, float]]) -> float:
        if not items:
            return 0.0
        total_vol = sum(sz for _, sz in items)
        if total_vol == 0:
            return items[0][0]
        return sum(p * sz for p, sz in items) / total_vol

    bid_dwa = depth_weighted_avg(bids)
    ask_dwa = depth_weighted_avg(asks)

    # convenience: aggregate into dataframes (optional)
    bids_df = pd.DataFrame(bids, columns=["price", "size"])
    asks_df = pd.DataFrame(asks, columns=["price", "size"])

    return {
        "best_bid": float(best_bid),
        "best_ask": float(best_ask),
        "spread": float(spread),
        "mid_price": float(mid_price),
        "bids": bids,
        "asks": asks,
        "bids_df": bids_df,
        "asks_df": asks_df,
        "total_bid_volume": float(total_bid_volume),
        "total_ask_volume": float(total_ask_volume),
        "bid_dwa": float(bid_dwa),
        "ask_dwa": float(ask_dwa),
    }
