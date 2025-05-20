import streamlit as st
import os
import time
import pandas as pd
from dotenv import load_dotenv
from collections import deque
from datetime import datetime
from ws_client import OrderBookClient
import io

load_dotenv()

URL = os.getenv("API_URL")

# 1) Initialize WebSocket client once
@st.cache_resource
def get_client(symbol):
    client = OrderBookClient(URL)
    client.subscribe_inst = symbol
    client.start()
    return client

# 2) Page + Sidebar
st.set_page_config(page_title="OKX Orderbook Dashboard", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    st.header("Input Parameters")
    exchange = st.selectbox("Exchange", options=["OKX"], index=0)
    symbol = st.selectbox("Spot Asset", options=["BTC-USDT"])
    order_type = st.selectbox("Order Type", options=["Market", "Limit"])
    quantity = st.number_input("Quantity (USD)", min_value=10.0, max_value=100000.0, value=100.0, step=10.0)
    volatility = st.slider("Volatility Estimate (%)", 0.1, 10.0, 1.5, 0.1)
    fee_tier = st.selectbox("Fee Tier", options=["Tier 1", "Tier 2", "Tier 3"])
    st.markdown("---")
    refresh_rate = st.slider("Refresh Interval (sec)", 0.5, 5.0, 1.0, 0.5)
    start_analysis = st.button("Start Analysis")
    st.markdown("---")
    st.header("Execution Simulation")
    simulate_order = st.button("Simulate Order Execution")

# 3) WebSocket & Charting Setup
client = get_client(symbol)

max_history = 60
times = deque(maxlen=max_history)
mid_prices = deque(maxlen=max_history)
spreads = deque(maxlen=max_history)
latencies = deque(maxlen=max_history)
health_statuses = deque(maxlen=max_history)

# Storage for data to export
export_data = []

# 4) Title
st.title(f"📊 OKX {symbol} Order Book")

# 5) Main Loop & Display

# Placeholder for dashboard content
placeholder = st.empty()

# Panel to display execution simulation results
exec_sim_placeholder = st.empty()

def check_health(latency_ms):
    if latency_ms < 100:
        return "Healthy", "✅"
    elif latency_ms < 300:
        return "Warning", "⚠️"
    else:
        return "Unhealthy", "❌"

try:
    if start_analysis:
        while True:
            data = client.get_latest_orderbook()
            latency = client.get_latency() * 1000
            now = datetime.utcnow()

            if data:
                times.append(now)
                mid_prices.append(data["mid_price"])
                spreads.append(data["spread"])
                latencies.append(latency)
                health, icon = check_health(latency)
                health_statuses.append(f"{icon} {health}")

                # Store row for export
                export_data.append({
                    "Time": now,
                    "Best Bid": data["best_bid"],
                    "Best Ask": data["best_ask"],
                    "Spread": data["spread"],
                    "Mid Price": data["mid_price"],
                    "Bid Volume": data["total_bid_volume"],
                    "Ask Volume": data["total_ask_volume"],
                    "Latency (ms)": latency,
                    "Health": health
                })

            with placeholder.container():
                # Metrics
                cols = st.columns(4)
                if data:
                    cols[0].metric("Best Bid", f"{data['best_bid']:.2f}")
                    cols[1].metric("Best Ask", f"{data['best_ask']:.2f}")
                    cols[2].metric("Spread", f"{data['spread']:.2f}")
                    cols[3].metric("Mid Price", f"{data['mid_price']:.2f}")

                    cols2 = st.columns(4)
                    cols2[0].metric("Bid Volume", f"{data['total_bid_volume']:.4f}")
                    cols2[1].metric("Ask Volume", f"{data['total_ask_volume']:.4f}")
                    cols2[2].metric("Latency (ms)", f"{latency:.1f}")
                    cols2[3].metric("Health Status", health_statuses[-1])

                else:
                    st.warning("Waiting for data...")

                st.markdown("---")

                # Charts
                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:
                    st.subheader("Mid Price Over Time")
                    df_mid = pd.DataFrame({
                        "Time": list(times),
                        "Mid Price": list(mid_prices)
                    })
                    df_mid = df_mid.set_index("Time")
                    st.line_chart(df_mid)

                with chart_col2:
                    st.subheader("Spread Over Time")
                    df_spread = pd.DataFrame({
                        "Time": list(times),
                        "Spread": list(spreads)
                    })
                    df_spread = df_spread.set_index("Time")
                    st.line_chart(df_spread)

                # Latency & Health Monitoring Panel
                st.subheader("Latency & Health Monitoring")
                df_latency = pd.DataFrame({
                    "Time": list(times),
                    "Latency (ms)": list(latencies),
                    "Health": list(health_statuses)
                })
                st.line_chart(df_latency[["Latency (ms)"]])
                st.write("Latest Health Status:", health_statuses[-1] if health_statuses else "N/A")

                # Export to CSV button
                if export_data:
                    df_export = pd.DataFrame(export_data)
                    csv_buffer = io.StringIO()
                    df_export.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label="Download Orderbook Data as CSV",
                        data=csv_buffer.getvalue(),
                        file_name=f"okx_orderbook_{symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )

            # Execution Simulation (simple logic)
            if simulate_order and data:
                # Simplified simulation: calculate estimated price for Market order or Limit order logic
                if order_type == "Market":
                    # Market orders filled at mid price +/- slippage from volatility
                    slippage = data["mid_price"] * volatility / 100
                    executed_price = data["mid_price"] + slippage if order_type == "Buy" else data["mid_price"] - slippage
                    exec_text = (
                        f"Simulated Market Order Execution:\n"
                        f"Quantity: ${quantity}\n"
                        f"Estimated Execution Price: {executed_price:.2f}\n"
                        f"Estimated Cost: ${quantity:.2f}"
                    )
                else:
                    # Limit order placed at best bid/ask with probability of fill affected by volatility
                    limit_price = data["best_ask"] if order_type == "Buy" else data["best_bid"]
                    exec_text = (
                        f"Simulated Limit Order:\n"
                        f"Quantity: ${quantity}\n"
                        f"Limit Price: {limit_price:.2f}\n"
                        f"Note: Execution depends on market movement and volatility."
                    )
                exec_sim_placeholder.code(exec_text)

            time.sleep(refresh_rate)

except KeyboardInterrupt:
    client.stop()
