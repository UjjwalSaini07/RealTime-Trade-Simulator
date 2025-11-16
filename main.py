# import streamlit as st
# import os
# import time
# import pandas as pd
# from dotenv import load_dotenv
# from collections import deque
# from datetime import datetime
# from ws_client import OrderBookClient
# import io

# load_dotenv()

# URL = os.getenv("API_URL")

# # 1) Initialize WebSocket client once
# @st.cache_resource
# def get_client(symbol):
#     client = OrderBookClient(URL)
#     client.subscribe_inst = symbol
#     client.start()
#     return client

# # 2) Page + Sidebar
# st.set_page_config(page_title="OKX Orderbook Dashboard", layout="wide", initial_sidebar_state="expanded")

# with st.sidebar:
#     st.header("Input Parameters")
#     exchange = st.selectbox("Exchange", options=["OKX"], index=0)
#     symbol = st.selectbox("Spot Asset", options=["BTC-USDT"])
#     order_type = st.selectbox("Order Type", options=["Market", "Limit"])
#     quantity = st.number_input("Quantity (USD)", min_value=10.0, max_value=100000.0, value=100.0, step=10.0)
#     volatility = st.slider("Volatility Estimate (%)", 0.1, 10.0, 1.5, 0.1)
#     fee_tier = st.selectbox("Fee Tier", options=["Tier 1", "Tier 2", "Tier 3"])
#     st.markdown("---")
#     refresh_rate = st.slider("Refresh Interval (sec)", 0.5, 5.0, 1.0, 0.5)
#     start_analysis = st.button("Start Analysis")
#     st.markdown("---")
#     st.header("Execution Simulation")
#     simulate_order = st.button("Simulate Order Execution")

# # 3) WebSocket & Charting Setup
# client = get_client(symbol)

# max_history = 60
# times = deque(maxlen=max_history)
# mid_prices = deque(maxlen=max_history)
# spreads = deque(maxlen=max_history)
# latencies = deque(maxlen=max_history)
# health_statuses = deque(maxlen=max_history)

# # Storage for data to export
# export_data = []

# # 4) Title
# st.title(f"📊 OKX {symbol} Order Book")

# # 5) Main Loop & Display

# # Placeholder for dashboard content
# placeholder = st.empty()

# # Panel to display execution simulation results
# exec_sim_placeholder = st.empty()

# def check_health(latency_ms):
#     if latency_ms < 100:
#         return "Healthy", "✅"
#     elif latency_ms < 300:
#         return "Warning", "⚠️"
#     else:
#         return "Unhealthy", "❌"

# try:
#     if start_analysis:
#         while True:
#             data = client.get_latest_orderbook()
#             latency = client.get_latency() * 1000
#             now = datetime.utcnow()

#             if data:
#                 times.append(now)
#                 mid_prices.append(data["mid_price"])
#                 spreads.append(data["spread"])
#                 latencies.append(latency)
#                 health, icon = check_health(latency)
#                 health_statuses.append(f"{icon} {health}")

#                 # Store row for export
#                 export_data.append({
#                     "Time": now,
#                     "Best Bid": data["best_bid"],
#                     "Best Ask": data["best_ask"],
#                     "Spread": data["spread"],
#                     "Mid Price": data["mid_price"],
#                     "Bid Volume": data["total_bid_volume"],
#                     "Ask Volume": data["total_ask_volume"],
#                     "Latency (ms)": latency,
#                     "Health": health
#                 })

#             with placeholder.container():
#                 # Metrics
#                 cols = st.columns(4)
#                 if data:
#                     cols[0].metric("Best Bid", f"{data['best_bid']:.2f}")
#                     cols[1].metric("Best Ask", f"{data['best_ask']:.2f}")
#                     cols[2].metric("Spread", f"{data['spread']:.2f}")
#                     cols[3].metric("Mid Price", f"{data['mid_price']:.2f}")

#                     cols2 = st.columns(4)
#                     cols2[0].metric("Bid Volume", f"{data['total_bid_volume']:.4f}")
#                     cols2[1].metric("Ask Volume", f"{data['total_ask_volume']:.4f}")
#                     cols2[2].metric("Latency (ms)", f"{latency:.1f}")
#                     cols2[3].metric("Health Status", health_statuses[-1])

#                 else:
#                     st.warning("Waiting for data...")

#                 st.markdown("---")

#                 # Charts
#                 chart_col1, chart_col2 = st.columns(2)

#                 with chart_col1:
#                     st.subheader("Mid Price Over Time")
#                     df_mid = pd.DataFrame({
#                         "Time": list(times),
#                         "Mid Price": list(mid_prices)
#                     })
#                     df_mid = df_mid.set_index("Time")
#                     st.line_chart(df_mid)

#                 with chart_col2:
#                     st.subheader("Spread Over Time")
#                     df_spread = pd.DataFrame({
#                         "Time": list(times),
#                         "Spread": list(spreads)
#                     })
#                     df_spread = df_spread.set_index("Time")
#                     st.line_chart(df_spread)

#                 # Latency & Health Monitoring Panel
#                 st.subheader("Latency & Health Monitoring")
#                 df_latency = pd.DataFrame({
#                     "Time": list(times),
#                     "Latency (ms)": list(latencies),
#                     "Health": list(health_statuses)
#                 })
#                 st.line_chart(df_latency[["Latency (ms)"]])
#                 st.write("Latest Health Status:", health_statuses[-1] if health_statuses else "N/A")

#                 # Export to CSV button
#                 if export_data:
#                     df_export = pd.DataFrame(export_data)
#                     csv_buffer = io.StringIO()
#                     df_export.to_csv(csv_buffer, index=False)
#                     st.download_button(
#                         label="Download Orderbook Data as CSV",
#                         data=csv_buffer.getvalue(),
#                         file_name=f"okx_orderbook_{symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
#                         mime="text/csv"
#                     )

#             # Execution Simulation (simple logic)
#             if simulate_order and data:
#                 # Simplified simulation: calculate estimated price for Market order or Limit order logic
#                 if order_type == "Market":
#                     # Market orders filled at mid price +/- slippage from volatility
#                     slippage = data["mid_price"] * volatility / 100
#                     executed_price = data["mid_price"] + slippage if order_type == "Buy" else data["mid_price"] - slippage
#                     exec_text = (
#                         f"Simulated Market Order Execution:\n"
#                         f"Quantity: ${quantity}\n"
#                         f"Estimated Execution Price: {executed_price:.2f}\n"
#                         f"Estimated Cost: ${quantity:.2f}"
#                     )
#                 else:
#                     # Limit order placed at best bid/ask with probability of fill affected by volatility
#                     limit_price = data["best_ask"] if order_type == "Buy" else data["best_bid"]
#                     exec_text = (
#                         f"Simulated Limit Order:\n"
#                         f"Quantity: ${quantity}\n"
#                         f"Limit Price: {limit_price:.2f}\n"
#                         f"Note: Execution depends on market movement and volatility."
#                     )
#                 exec_sim_placeholder.code(exec_text)

#             time.sleep(refresh_rate)

# except KeyboardInterrupt:
#     client.stop()



# !!
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

@st.cache_resource
def get_client(url):
    client = OrderBookClient(url)
    client.start()
    return client

st.set_page_config(page_title="OKX Orderbook Dashboard", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    st.header("Input Parameters")
    exchange = st.selectbox("Exchange", options=["OKX"], index=0)
    symbol = st.selectbox("Spot Asset", options=["BTC-USDT"], index=0)
    # separate Order Side + Order Type (fix bug in original)
    order_side = st.selectbox("Side", options=["Buy", "Sell"])
    order_type = st.selectbox("Order Type", options=["Market", "Limit"])
    quantity = st.number_input("Quantity (USD)", min_value=1.0, max_value=1_000_000.0, value=100.0, step=1.0, format="%.2f")
    volatility = st.slider("Volatility Estimate (%)", 0.1, 10.0, 1.5, 0.1)
    fee_tier = st.selectbox("Fee Tier", options=["Tier 1", "Tier 2", "Tier 3"])
    st.markdown("---")
    refresh_rate = st.slider("Refresh Interval (sec)", 0.5, 5.0, 1.0, 0.5)

    # start / stop controls use session state (toggle buttons)
    if "running" not in st.session_state:
        st.session_state.running = False
    start_btn = st.button("▶ Start Live")
    stop_btn = st.button("■ Stop Live")
    st.markdown("---")
    st.header("Execution Simulation")
    simulate_order = st.checkbox("Show simulation panel", value=False)
    st.markdown("Simulation uses current orderbook snapshot and volatility to estimate fills.")

# attach client and set subscription if changed
client = get_client(URL)
# update client subscription if symbol changed
if getattr(client, "subscribe_inst", None) != symbol:
    client.subscribe_inst = symbol

max_history = 120  # store last N samples
def init_state():
    if "times" not in st.session_state:
        st.session_state.times = deque(maxlen=max_history)
    if "mid_prices" not in st.session_state:
        st.session_state.mid_prices = deque(maxlen=max_history)
    if "spreads" not in st.session_state:
        st.session_state.spreads = deque(maxlen=max_history)
    if "latencies" not in st.session_state:
        st.session_state.latencies = deque(maxlen=max_history)
    if "health_statuses" not in st.session_state:
        st.session_state.health_statuses = deque(maxlen=max_history)
    if "export_data" not in st.session_state:
        st.session_state.export_data = []
    if "last_data" not in st.session_state:
        st.session_state.last_data = None

init_state()

# handle start/stop toggle
if start_btn:
    st.session_state.running = True
if stop_btn:
    st.session_state.running = False

# Small helper for health
def check_health(latency_ms):
    if latency_ms < 100:
        return "Healthy", "✅"
    elif latency_ms < 300:
        return "Warning", "⚠️"
    else:
        return "Unhealthy", "❌"

# UI skeleton: title + placeholders
st.title(f"📊 OKX {symbol} Order Book Dashboard")
top_placeholder = st.container()          # for metrics
chart_placeholder = st.container()        # for charts
table_placeholder = st.container()        # for raw orderbook / export
sim_placeholder = st.container()          # for simulation text

# If not running, show last snapshot and a friendly message
if not st.session_state.running:
    with top_placeholder:
        st.info("Live feed is stopped — press ▶ Start Live to begin real-time updates.")
        if st.session_state.last_data is None:
            st.warning("No data yet. Start live to fetch the first snapshot.")
    # still show historical charts if any
    if st.session_state.times:
        with chart_placeholder:
            tab1, tab2 = st.tabs(["Charts", "Latency & Health"])
            with tab1:
                st.subheader("Mid Price (historic)")
                df_mid = pd.DataFrame({"Time": list(st.session_state.times), "Mid Price": list(st.session_state.mid_prices)}).set_index("Time")
                st.line_chart(df_mid)
                st.subheader("Spread (historic)")
                df_spread = pd.DataFrame({"Time": list(st.session_state.times), "Spread": list(st.session_state.spreads)}).set_index("Time")
                st.line_chart(df_spread)
            with tab2:
                st.subheader("Latency (historic)")
                df_latency = pd.DataFrame({"Time": list(st.session_state.times), "Latency (ms)": list(st.session_state.latencies)}).set_index("Time")
                st.line_chart(df_latency)
                st.write("Latest Health:", st.session_state.health_statuses[-1] if st.session_state.health_statuses else "N/A")
    # show last raw snapshot + export if available
    with table_placeholder:
        if st.session_state.last_data:
            st.subheader("Last Orderbook Snapshot")
            st.json(st.session_state.last_data)
        if st.session_state.export_data:
            df_export = pd.DataFrame(st.session_state.export_data)
            st.dataframe(df_export.tail(50))
            csv_buffer = io.StringIO()
            df_export.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download Orderbook Data as CSV",
                data=csv_buffer.getvalue(),
                file_name=f"okx_orderbook_{symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    # show simulation panel if requested (uses last_data snapshot)
    with sim_placeholder:
        if simulate_order:
            if st.session_state.last_data:
                data = st.session_state.last_data
            else:
                st.warning("No data available for simulation. Start live to gather data.")
                data = None
            if data:
                # run simulation (same logic but fixed)
                if order_type == "Market":
                    slippage = data["mid_price"] * volatility / 100
                    executed_price = data["mid_price"] + slippage if order_side == "Buy" else data["mid_price"] - slippage
                    est_cost = quantity  # user passed USD quantity; you might adapt this
                    st.code(
                        f"Simulated Market {order_side} Order\n"
                        f"Quantity: ${quantity:.2f}\n"
                        f"Estimated Execution Price: {executed_price:.2f}\n"
                        f"Estimated Cost (USD): ${est_cost:.2f}\n"
                        f"Slippage used: {slippage:.4f}"
                    )
            else:
                st.info("Simulation will activate once data is available.")

    st.stop()  # stop further execution when not running

try:
    data = client.get_latest_orderbook()
    latency = client.get_latency() * 1000  # ms
    now = datetime.utcnow()

    if data:
        # store current snapshot for quick access & export
        st.session_state.last_data = data

        st.session_state.times.append(now)
        st.session_state.mid_prices.append(data["mid_price"])
        st.session_state.spreads.append(data["spread"])
        st.session_state.latencies.append(latency)
        health, icon = check_health(latency)
        st.session_state.health_statuses.append(f"{icon} {health}")

        st.session_state.export_data.append({
            "Time": now.isoformat(),
            "Best Bid": data.get("best_bid"),
            "Best Ask": data.get("best_ask"),
            "Spread": data.get("spread"),
            "Mid Price": data.get("mid_price"),
            "Bid Volume": data.get("total_bid_volume"),
            "Ask Volume": data.get("total_ask_volume"),
            "Latency (ms)": latency,
            "Health": health
        })

    # Render top metrics
    with top_placeholder:
        cols = st.columns([1,1,1,1])
        if data:
            # compute small deltas for metrics (if previous exists)
            prev_mid = st.session_state.mid_prices[-2] if len(st.session_state.mid_prices) > 1 else None
            mid_delta = (data["mid_price"] - prev_mid) if prev_mid is not None else 0.0
            cols[0].metric("Best Bid", f"{data['best_bid']:.2f}", delta=None)
            cols[1].metric("Best Ask", f"{data['best_ask']:.2f}", delta=None)
            cols[2].metric("Spread", f"{data['spread']:.2f}", delta=None)
            cols[3].metric("Mid Price", f"{data['mid_price']:.2f}", delta=f"{mid_delta:.2f}")

        else:
            st.warning("No orderbook snapshot received yet. Waiting for websocket data...")

        # second row of metrics
        cols2 = st.columns([1,1,1,1])
        if data:
            cols2[0].metric("Bid Volume", f"{data['total_bid_volume']:.6f}")
            cols2[1].metric("Ask Volume", f"{data['total_ask_volume']:.6f}")
            cols2[2].metric("Latency (ms)", f"{latency:.1f}")
            cols2[3].metric("Health", st.session_state.health_statuses[-1])
        st.progress(min(1.0, len(st.session_state.times)/max_history))

    # Charts & tables
    with chart_placeholder:
        tab1, tab2, tab3 = st.tabs(["Price & Spread", "Latency & Health", "Orderbook Snapshot"])
        with tab1:
            st.subheader("Mid Price Over Time")
            df_mid = pd.DataFrame({"Time": list(st.session_state.times), "Mid Price": list(st.session_state.mid_prices)}).set_index("Time")
            st.line_chart(df_mid)
            st.subheader("Spread Over Time")
            df_spread = pd.DataFrame({"Time": list(st.session_state.times), "Spread": list(st.session_state.spreads)}).set_index("Time")
            st.line_chart(df_spread)
        with tab2:
            st.subheader("Latency (ms) Over Time")
            df_latency = pd.DataFrame({"Time": list(st.session_state.times), "Latency (ms)": list(st.session_state.latencies)}).set_index("Time")
            st.line_chart(df_latency)
            st.write("Live Health Status:", st.session_state.health_statuses[-1])
        with tab3:
            st.subheader("Latest Raw Orderbook Snapshot")
            if data:
                left, right = st.columns(2)
                with left:
                    st.write("Top bids (best first)")
                    bids = data.get("bids", [])[:10]
                    st.table(pd.DataFrame(bids, columns=["Price", "Qty"]))
                with right:
                    st.write("Top asks (best first)")
                    asks = data.get("asks", [])[:10]
                    st.table(pd.DataFrame(asks, columns=["Price", "Qty"]))
            else:
                st.info("No snapshot to show yet.")

    # Export area
    with table_placeholder:
        if st.session_state.export_data:
            df_export = pd.DataFrame(st.session_state.export_data)
            st.dataframe(df_export.tail(20))
            csv_buffer = io.StringIO()
            df_export.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download Orderbook Data as CSV",
                data=csv_buffer.getvalue(),
                file_name=f"okx_orderbook_{symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    # Simulation panel
    with sim_placeholder:
        if simulate_order:
            if st.session_state.last_data:
                data = st.session_state.last_data
                if order_type == "Market":
                    slippage = data["mid_price"] * volatility / 100
                    executed_price = data["mid_price"] + slippage if order_side == "Buy" else data["mid_price"] - slippage
                    est_cost = quantity
                    st.info("Market order simulation (estimated)")
                    st.write(f"- Side: {order_side}")
                    st.write(f"- Quantity (USD): {quantity:.2f}")
                    st.write(f"- Estimated Execution Price: {executed_price:.2f}")
                    st.write(f"- Estimated Cost (USD): {est_cost:.2f}")
                    st.write(f"- Slippage used: {slippage:.6f}")
                else:
                    limit_price = data["best_ask"] if order_side == "Buy" else data["best_bid"]
                    st.info("Limit order simulation (probabilistic)")
                    st.write(f"- Side: {order_side}")
                    st.write(f"- Quantity (USD): {quantity:.2f}")
                    st.write(f"- Suggested Limit Price: {limit_price:.2f}")
                    st.write("- Note: Execution probability depends on market movement & volatility.")
            else:
                st.warning("No orderbook snapshot yet for simulation.")

    # wait & rerun cycle
    time.sleep(refresh_rate)
    # Keep auto-run while the toggle is on. This triggers a rerun and produces the next sample.
    if st.session_state.running:
        st.experimental_rerun()

except Exception as e:
    st.error(f"Error in live loop: {e}")
    # attempt a graceful shutdown of client on fatal error
    try:
        client.stop()
    except Exception:
        pass
