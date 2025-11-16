import os
import time
from dotenv import load_dotenv
from ws_client import OrderBookClient

load_dotenv()

URL = os.getenv("API_URL")

def main():
    client = OrderBookClient(URL)
    client.start()

    try:
        while True:
            data = client.get_latest_orderbook()
            if data:
                print("Latest orderbook data:", data)
            else:
                print("No data yet")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping client...")
        client.stop()

if __name__ == "__main__":
    main()


#! TEST FILE FOR OrderBookProcessor
# from ws_client import OrderBookClient
# from orderbook_processor import OrderBookProcessor
# import time

# client = OrderBookClient("wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP")
# processor = OrderBookProcessor()
# client.start()

# time.sleep(3)

# latest = client.get_latest_orderbook()
# processed = processor.update(latest)
# if processed is not None:
#     print("\n📊 Processed Orderbook Data:")
#     print(processed)
# else:
#     print("[Info] Skipped an invalid orderbook tick.")
#     print("No data yet")

# client.stop()
