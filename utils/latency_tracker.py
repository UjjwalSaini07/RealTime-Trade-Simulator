import time
from collections import deque

class LatencyTracker:
    """
    Track latency samples and provide smoothed statistics.
    """
    def __init__(self, max_samples=100):
        self.latencies = deque(maxlen=max_samples)

    def add_latency(self, latency_ms: float):
        self.latencies.append(latency_ms)

    def average_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    def max_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return max(self.latencies)

    def clear(self):
        self.latencies.clear()
