import pandas as pd

def process_orderbook_snapshot(snapshot: dict) -> dict:
    asks = snapshot.get("asks", [])
    bids = snapshot.get("bids", [])

    if not asks or not bids:
        return {}

    best_ask = float(asks[0][0])
    best_bid = float(bids[0][0])
    spread = best_ask - best_bid
    mid_price = (best_ask + best_bid) / 2
    total_ask_volume = sum(float(a[1]) for a in asks)
    total_bid_volume = sum(float(b[1]) for b in bids)

    return {
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": spread,
        "mid_price": mid_price,
        "total_ask_volume": total_ask_volume,
        "total_bid_volume": total_bid_volume,
    }
