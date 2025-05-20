# 📈 OKX Real-Time Orderbook Analysis & Execution Simulator

A Streamlit-based real-time trading dashboard for analyzing the OKX spot orderbook, simulating execution strategies, tracking latency, visualizing price spreads, and modeling slippage and market impact, it connects to the OKX WebSocket API to stream live order book data for selected spot assets. It provides real-time visualization of market depth metrics such as best bid/ask, spread, mid-price, volumes, latency monitoring, health status, and simulates basic order execution scenarios.
**The goal** is to enable traders and analysts to monitor market liquidity and simulate order executions interactively in a clean, easy-to-use web interface.

## 🚀 Features

- 📡 Real-time WebSocket order book data from OKX WebSocket API (books5 channel)
- 📊 Mid-price & spread time series visualization
- ⚡ Latency & system health monitoring
- 🎯 Market/Limit execution simulation with volatility
- 🧠 Model-based slippage prediction & market impact estimation
- 💻 Display of key metrics:
  - Best Bid and Best Ask prices
  - Bid/Ask volumes
  - Spread and Mid Price over time
  - Latency measurement and health monitoring (Healthy / Warning / Unhealthy)
- 🗎 Interactive parameter inputs including symbol, order type, quantity, volatility estimate, fee tiers, and refresh rate
- 💾 CSV export of historical order book data
- 📎 Modular architecture: `models/`, `utils/`, `ws_client.py`

## 🗂️ Project Structure

```bash
okx_assignment/
│
├── main.py                    # Streamlit app (UI + logic)
├── ws_client.py              # WebSocket client for orderbook
│
├── models/
│   ├── slippage_model.py     # Linear regression for slippage
│   ├── market_impact.py      # Almgren–Chriss model
│   └── maker_taker_model.py  # Logistic regression: maker vs taker
│
├── utils/
│   ├── latency_tracker.py    # Tracks system/network latency
│   ├── fee_model.py          # Tiered fee computation
│   └── data_utils.py         # Preprocess orderbook data
│
├── .env                      # Environment Variables
├── test_ws.py                # TestModule File
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation (this file)
```

## Architecture

- **_main.py_** : Main Streamlit application responsible for the user interface, real-time order book visualization, trading simulation, model interaction, and export functionalities.
- **_ws_client.py_** : WebSocket client managing the connection to OKX's public WebSocket API. Handles subscription, reconnection logic, and parsing of live order book data.
- **_models/slippage_model.py_** : Implements a linear regression model to estimate slippage based on order size and market depth.
- **_models/market_impact.py_** : Applies the Almgren–Chriss model to evaluate the market impact of large trades over time.
- **_models/maker_taker_model.py_** : Uses logistic regression to predict whether a trade will be a maker or taker based on live order book features.
- **_utils/latency_tracker.py_** : Measures and logs system and network latency to monitor real-time performance.
- **_utils/fee_model.py_** : Calculates trading fees based on tiered fee structure, accounting for maker and taker differences.
- **_utils/data_utils.py_** : Provides utility functions for preprocessing and structuring order book data.
- **_.env_** : Environment configuration file storing sensitive data such as WebSocket URLs or API credentials.
- **_requirements.txt_** : Lists all Python dependencies required to install and run the application.
- **_test_ws.py_** : Standalone test script to validate WebSocket connectivity and data integrity.
- **_README.md_** : Documentation file providing an overview, setup instructions, and project structure.
