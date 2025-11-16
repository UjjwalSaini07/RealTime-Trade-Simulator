import time
from collections import deque
import statistics
from typing import Deque, List, Optional

class LatencyTracker:
    def __init__(self, max_samples: int = 500):
        self.latencies: Deque[float] = deque(maxlen=max_samples)

    def add_latency(self, latency_ms: float):
        if latency_ms is None:
            return
        try:
            val = float(latency_ms)
        except Exception:
            return
        self.latencies.append(val)

    def average_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return float(sum(self.latencies) / len(self.latencies))

    def median_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return float(statistics.median(self.latencies))

    def p95_latency(self) -> float:
        if not self.latencies:
            return 0.0
        arr = sorted(self.latencies)
        idx = int(0.95 * (len(arr) - 1))
        return float(arr[idx])

    def max_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return float(max(self.latencies))

    def clear(self):
        self.latencies.clear()

    def health_status(self) -> str:
        p95 = self.p95_latency()
        if p95 == 0:
            return "Unknown"
        if p95 < 100:
            return "Healthy"
        if p95 < 300:
            return "Warning"
        return "Unhealthy"
