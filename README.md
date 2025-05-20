# 📈 OKX Real-Time Orderbook Analysis & Execution Simulator

A Streamlit-based real-time trading dashboard for analyzing the OKX spot orderbook, simulating execution strategies, tracking latency, visualizing price spreads, and modeling slippage and market impact, it connects to the OKX WebSocket API to stream live order book data for selected spot assets. It provides real-time visualization of market depth metrics such as best bid/ask, spread, mid-price, volumes, latency monitoring, health status, and simulates basic order execution scenarios.
**The goal** is to enable traders and analysts to monitor market liquidity and simulate order executions interactively in a clean, easy-to-use web interface.

## Features 🚀

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

## Project Structure 🗂️ 

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

## Installation 🛠️
1. Navigate to the project Root directory:
```bash
cd okx_assignment
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Create a .env file in the root directory
```bash
API_URL=wss://ws.okx.com:8443/ws/v5/public
```

# Usage 🖥️
- Run the Streamlit app:
```bash
python -m streamlit run main.py
```
- The dashboard will open in your default browser: http://localhost:8501/

## Dashboard Panels
- **_Metrics_**: Shows current best bid/ask, spread, mid price, bid/ask volumes, latency, and health status.
- **_Charts_**: Real-time line charts for mid price, spread, and latency over time.
- **_Latency & Health Monitoring_**: Shows latency trends and health status based on latency thresholds.
- **_Execution Simulation_**: Displays simulated execution results based on order type and market conditions.
- **_Export Data_**: Button to download historical order book snapshots and metrics as CSV.

## Model Documentation 🧠

### 1. Slippage Model (`models/slippage_model.py`)
- **Model Used**: Linear Regression  
- **Purpose**: Estimate price deviation based on order size, volatility, and spread.  
- **Features**:
  - `order_size_usd`
  - `market_volatility`
  - `spread_percent`  
- **Target**: `slippage_bps` (slippage in basis points)

### 2. Market Impact Model (`models/market_impact.py`)
- **Methodology**: Almgren–Chriss Framework  
- **Assumptions**:
  - Temporary and permanent impact modeled with linear coefficients  
  - Market volume as liquidity proxy  
- **Equation**:  
  `impact = η * (Q / V) + λ * (Q / V)^2`  
  Where:  
  - `Q`: order size  
  - `V`: market volume  
  - `η`, `λ`: impact coefficients  

### 3. Maker vs Taker Model (`models/maker_taker_model.py`)
- **Model Used**: Logistic Regression  
- **Purpose**: Predict execution likelihood for limit orders.  
- **Features**:
  - `spread`
  - `volatility`
  - `order_type`
  - `relative_price_distance`

## Utility Modules 🧰 

#### 1. `utils/latency_tracker.py` : Measures roundtrip latency for WebSocket events and internal app cycles.
#### 2. `utils/fee_model.py` : Supports tiered maker-taker fee structures (OKX Tier 1, 2, 3).
#### 3. `utils/data_utils.py` : Converts OKX order book ticks into normalized pandas DataFrames.

## Performance Optimization ⚙️

- `@st.cache_resource` to avoid re-instantiating WebSocket clients  
- `deque` with `maxlen` for lightweight time series  
- DataFrames rebuilt only from live updates  
- Streamlit container reuse to reduce render load


## Future Enhancements 🧭

| Feature | Description |
|--------|-------------|
| 🔌 FastAPI Backend | Refactor core logic into a FastAPI backend to support RESTful and WebSocket endpoints for scalable API-based integration. |
| 📱 Mobile Dashboard | Build a responsive frontend using React Native or Flutter to access real-time analytics from mobile devices. |
| 📦 Redis Caching Layer | Introduce Redis for efficient storage and retrieval of real-time market data and reduce load on WebSocket listeners. |
| 📈 Historical Backtesting Engine | Implement a module for backtesting execution strategies using historical tick data. |
| 🔐 User Authentication | Add secure login with role-based access (e.g., admin vs. analyst) using OAuth2 or Firebase. |
| 🧪 CI/CD & Dockerization | Containerize the entire system and set up CI/CD pipelines with GitHub Actions and Docker Compose. |

## Contact 📞
Feel free to reach out if you have any questions or suggestions!

- Email: [Mail](ujjwalsaini0007@gmail.com)
- Github: [@Ujjwal Saini](https://github.com/UjjwalSaini07)

## Screenshots 📷
### Trading Dashboard
![image](https://github.com/user-attachments/assets/94c961c9-6d48-4d72-823c-255d746def22)

### Terminal Data Retrieval
![image](https://github.com/user-attachments/assets/f33ea2fd-dde1-4486-a90a-6c429bcd0c75)

<div align="center">
    <a href="#top">
        <img src="https://img.shields.io/badge/Back%20to%20Top-000000?style=for-the-badge&logo=github&logoColor=white" alt="Back to Top">
    </a>
</div>






