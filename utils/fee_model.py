class FeeModel:
    # Example fee structure; replace with actual exchange fee tiers
    FEE_TABLE = {
        "Tier 1": {"maker": 0.001, "taker": 0.002},
        "Tier 2": {"maker": 0.0008, "taker": 0.0015},
        "Tier 3": {"maker": 0.0005, "taker": 0.001},
    }

    def __init__(self, tier="Tier 1"):
        if tier not in self.FEE_TABLE:
            raise ValueError(f"Unknown fee tier: {tier}")
        self.tier = tier
        self.maker_fee = self.FEE_TABLE[tier]["maker"]
        self.taker_fee = self.FEE_TABLE[tier]["taker"]

    def calculate_fee(self, volume: float, is_maker: bool) -> float:
        fee_rate = self.maker_fee if is_maker else self.taker_fee
        return volume * fee_rate
