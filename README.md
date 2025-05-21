# 📈 RealTime Trade Simulator & Orderbook Analysis
A Streamlit-based real-time trading dashboard for analyzing the OKX spot orderbook, simulating execution strategies, tracking latency, visualizing price spreads, and modeling slippage and market impact, it connects to the OKX WebSocket API to stream live order book data for selected spot assets. It provides real-time visualization of market depth metrics such as best bid/ask, spread, mid-price, volumes, latency monitoring, health status, and simulates basic order execution scenarios.
**The goal** is to enable traders and analysts to monitor market liquidity and simulate order executions interactively in a clean, easy-to-use web interface.

[![Github License](https://img.shields.io/github/license/UjjwalSaini07/RealTime-Trade-Simulator)](https://github.com/UjjwalSaini07/RealTime-Trade-Simulator/blob/main/LICENSE)
[![Info](https://img.shields.io/badge/Project-Info-blue?style=flat&logo=data:image/svg%2bxml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pg0KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDE5LjAuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4gU1ZHIFZlcnNpb246IDYuMDAgQnVpbGQgMCkgIC0tPg0KPHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJDYXBhXzEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjBweCIgeT0iMHB4Ig0KCSB2aWV3Qm94PSIwIDAgNTEyIDUxMiIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgNTEyIDUxMjsiIHhtbDpzcGFjZT0icHJlc2VydmUiPg0KPHBhdGggc3R5bGU9ImZpbGw6IzBBNEVBRjsiIGQ9Ik0yNTYsNTEyYy02OC4zOCwwLTEzMi42NjctMjYuNjI5LTE4MS4wMi03NC45OEMyNi42MjksMzg4LjY2NywwLDMyNC4zOCwwLDI1Ng0KCVMyNi42MjksMTIzLjMzMyw3NC45OCw3NC45OEMxMjMuMzMzLDI2LjYyOSwxODcuNjIsMCwyNTYsMHMxMzIuNjY3LDI2LjYyOSwxODEuMDIsNzQuOThDNDg1LjM3MSwxMjMuMzMzLDUxMiwxODcuNjIsNTEyLDI1Ng0KCXMtMjYuNjI5LDEzMi42NjctNzQuOTgsMTgxLjAyQzM4OC42NjcsNDg1LjM3MSwzMjQuMzgsNTEyLDI1Niw1MTJ6Ii8+DQo8cGF0aCBzdHlsZT0iZmlsbDojMDYzRThCOyIgZD0iTTQzNy4wMiw3NC45OEMzODguNjY3LDI2LjYyOSwzMjQuMzgsMCwyNTYsMHY1MTJjNjguMzgsMCwxMzIuNjY3LTI2LjYyOSwxODEuMDItNzQuOTgNCglDNDg1LjM3MSwzODguNjY3LDUxMiwzMjQuMzgsNTEyLDI1NlM0ODUuMzcxLDEyMy4zMzMsNDM3LjAyLDc0Ljk4eiIvPg0KPHBhdGggc3R5bGU9ImZpbGw6I0ZGRkZGRjsiIGQ9Ik0yNTYsMTg1Yy0zMC4zMjcsMC01NS0yNC42NzMtNTUtNTVzMjQuNjczLTU1LDU1LTU1czU1LDI0LjY3Myw1NSw1NVMyODYuMzI3LDE4NSwyNTYsMTg1eiBNMzAxLDM5NQ0KCVYyMTVIMTkxdjMwaDMwdjE1MGgtMzB2MzBoMTQwdi0zMEgzMDF6Ii8+DQo8Zz4NCgk8cGF0aCBzdHlsZT0iZmlsbDojQ0NFRkZGOyIgZD0iTTI1NiwxODVjMzAuMzI3LDAsNTUtMjQuNjczLDU1LTU1cy0yNC42NzMtNTUtNTUtNTVWMTg1eiIvPg0KCTxwb2x5Z29uIHN0eWxlPSJmaWxsOiNDQ0VGRkY7IiBwb2ludHM9IjMwMSwzOTUgMzAxLDIxNSAyNTYsMjE1IDI1Niw0MjUgMzMxLDQyNSAzMzEsMzk1IAkiLz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjwvc3ZnPg0K)](https://github.com/UjjwalSaini07/RealTime-Trade-Simulator/blob/main/README.md)
[![Generic badge](https://img.shields.io/badge/Owner-@Ujjwal-<COLOR>.svg)](https://github.com/UjjwalSaini07/RealTime-Trade-Simulator)
[![GitHub stars](https://img.shields.io/github/stars/UjjwalSaini07/RealTime-Trade-Simulator?style=social&label=Star&maxAge=2592100)](https://github.com/UjjwalSaini07/RealTime-Trade-Simulator)
[![Github Release](https://img.shields.io/github/v/release/UjjwalSaini07/RealTime-Trade-Simulator)](https://github.com/UjjwalSaini07/RealTime-Trade-Simulator)

## Features 🚀

- 📡 Real-time WebSocket order book data from OKX WebSocket API (books5 channel)
- 📊 Mid-price & spread time series visualization
- ⚡ Latency & system health monitoring
- 🎯 Market/Limit execution simulation with volatility
- 🧠 Model-based slippage prediction & market impact estimation
- 🗎 Interactive parameter inputs- symbol, order type, quantity, volatility estimate, fee tiers, and refresh rate
- 💾 CSV export of historical order book data
- 📎 Modular architecture: `models/`, `utils/`, `ws_client.py`
- 💻 Display of key metrics:
  - Best Bid and Best Ask prices
  - Bid/Ask volumes
  - Spread and Mid Price over time
  - Latency measurement and health monitoring (Healthy / Warning / Unhealthy)

## Project Structure 🗂️ 

```bash
RealTime-Trade-Simulator/
│
├── main.py                   # Streamlit app (UI + logic)
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
- First Read this [License](https://github.com/UjjwalSaini07/RealTime-Trade-Simulator/blob/main/LICENSE) & their terms then proceed.
- Star ⭐ the [Repository](https://github.com/UjjwalSaini07/RealTime-Trade-Simulator)
- Fork the repository **(Optional)**
- Project Setup:
1. Clone the Project
```bash
git clone https://github.com/UjjwalSaini07/RealTime-Trade-Simulator.git
```
2. Navigate to the project Root directory:
```bash
cd RealTime-Trade-Simulator
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Create a .env file in the root directory and Setup [Contact](mailto:ujjwalsaini0007+envreq@gmail.com)

# Usage 🖥️
- Run the Streamlit app:
```bash
python -m streamlit run main.py
```
- The dashboard will open in your default browser: http://localhost:8501/

## Project Setup Using Docker Containerization:
1. Start the Docker Engine Locally or Use Any Service
2. Navigate to the project Root directory:
```bash
    cd RealTime-Trade-Simulator
```
3. Run DockerFile:
```bash
    docker-compose up --build
```
4. Wait for Generating the Image
#### How Docker Image Builds Looks

  ![image](https://github.com/user-attachments/assets/313cbbc6-a55a-45a5-bcde-ecc218aa8080)

#### Docker Image Starts the Server Locally

  ![image](https://github.com/user-attachments/assets/44e594fb-0200-47de-beff-0c627af5df5f)

#### Project Docker Container WebSockets Data Fetching

  ![image](https://github.com/user-attachments/assets/79e7e298-1fe5-4509-ae7d-06e065e3c0e2)

5. Now Simply use the Project using Docker Container

## Dashboard Panels
- **_Metrics_**: Shows current best bid/ask, spread, mid price, bid/ask volumes, latency, and health status.
- **_Charts_**: Real-time line charts for mid price, spread, and latency over time.
- **_Latency & Health Monitoring_**: Shows latency trends and health status based on latency thresholds.
- **_Execution Simulation_**: Displays simulated execution results based on order type and market conditions.
- **_Export Data_**: Button to download historical order book snapshots and metrics as CSV.

## Model Documentation 🧠

### 1. Slippage Model
**Path**: `models/slippage_model.py`  
- **Model**: Linear Regression  
- **Purpose**: Estimate price deviation from order size, volatility, and spread.  
- **Features**: `order_size_usd`, `market_volatility`, `spread_percent`  
- **Target**: `slippage_bps`  

### 2. Market Impact Model
**Path**: `models/market_impact.py`  
- **Framework**: Almgren–Chriss  
- **Assumptions**:  
  - Linear coefficients for temporary and permanent impact  
  - Liquidity proxy via market volume  
- **Equation**:  
  `impact = η * (Q / V) + λ * (Q / V)^2`  
  - `Q`: order size  
  - `V`: market volume  
  - `η`, `λ`: impact coefficients  

### 3. Maker vs Taker Model
**Path**: `models/maker_taker_model.py`  
- **Model**: Logistic Regression  
- **Purpose**: Predict limit order execution likelihood.  
- **Features**: `spread`, `volatility`, `order_type`, `relative_price_distance`


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

## Video Demonstration 📷

[Project Demonstration](https://github.com/user-attachments/assets/9731901b-7946-4a50-94c6-80a739fa0be4)

<div align="center">
    <a href="#top">
        <img src="https://img.shields.io/badge/Back%20to%20Top-000000?style=for-the-badge&logo=github&logoColor=white" alt="Back to Top">
    </a>
</div>

