import websocket
import threading
import json
import time
from loguru import logger

class OrderBookClient:
    def __init__(self, url):
        self.url = url
        self.ws = None
        self.running = False
        self.latest_data = None
        self.latest_latency_ms = None

    def _process_orderbook(self, data):
        try:
            asks = data.get('asks', [])
            bids = data.get('bids', [])
            if not asks or not bids:
                logger.warning("Empty asks or bids in orderbook data")
                return None

            best_ask = float(asks[0][0])
            best_bid = float(bids[0][0])

            if best_bid >= best_ask:
                logger.warning("Invalid orderbook tick: best bid >= best ask")
                return None

            spread = best_ask - best_bid
            mid_price = (best_ask + best_bid) / 2

            total_ask_volume = sum(float(item[1]) for item in asks)
            total_bid_volume = sum(float(item[1]) for item in bids)

            processed = {
                "best_bid": best_bid,
                "best_ask": best_ask,
                "spread": spread,
                "mid_price": mid_price,
                "total_ask_volume": total_ask_volume,
                "total_bid_volume": total_bid_volume,
                "instId": data.get("instId"),
                "ts": data.get("ts"),
            }

            return processed

        except Exception as e:
            logger.error(f"Error processing orderbook data: {e}")
            return None

    def _on_message(self, ws, message):
        start = time.time()

        try:
            data = json.loads(message)

            if 'arg' in data and data['arg'].get('channel') == 'books5':
                if 'data' in data and len(data['data']) > 0:
                    orderbook = data['data'][0]
                    processed = self._process_orderbook(orderbook)

                    if processed is None:
                        logger.warning("[Info] Skipped invalid or incomplete orderbook data.")
                        return

                    self.latest_data = processed

                    end = time.time()
                    self.latest_latency_ms = round((end - start) * 1000, 3)

                    logger.info(
                        f"Processed tick: Best Bid={processed['best_bid']}, "
                        f"Best Ask={processed['best_ask']}, Spread={processed['spread']:.2f}, "
                        f"Latency={self.latest_latency_ms} ms"
                    )
                else:
                    logger.warning("Received empty orderbook data")
            else:
                logger.debug(f"Message received: {data}")

        except Exception as e:
            logger.error(f"Error parsing message: {e}")

    def _on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        logger.warning("WebSocket closed")

    def _on_open(self, ws):
        logger.info("WebSocket connection opened")
        subscribe_message = {
            "op": "subscribe",
            "args": [
                {
                    "channel": "books5",
                    "instId": "BTC-USDT"
                }
            ]
        }
        ws.send(json.dumps(subscribe_message))

    def start(self):
        self.running = True
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )

        self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.thread.start()
        logger.info("WebSocket client thread started")

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()

    def get_latest_orderbook(self):
        return self.latest_data

    def get_latency(self):
        return self.latest_latency_ms
