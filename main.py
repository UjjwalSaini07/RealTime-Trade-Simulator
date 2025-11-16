import streamlit as st
import os
import time
import pandas as pd
from dotenv import load_dotenv
from collections import deque
from datetime import datetime, timezone  
from ws_client import OrderBookClient
import io
import altair as alt

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
    exchange = st.selectbox(
        "Exchange",
        options=["OKX"],
        index=0,
        help="Select the exchange source for orderbook data (currently only OKX supported)."
    )
    symbol = st.selectbox(
        "Spot Asset",
        options=["BTC-USDT"],
        index=0,
        help="Trading pair / instrument to subscribe to (e.g., BTC-USDT)."
    )
    order_side = st.selectbox(
        "Side",
        options=["Buy", "Sell"],
        help="Direction of the simulated order: Buy or Sell."
    )
    order_type = st.selectbox(
        "Order Type",
        options=["Market", "Limit"],
        help="Market executes immediately at market price; Limit posts an order at a chosen price."
    )
    quantity = st.number_input(
        "Quantity (USD)",
        min_value=1.0,
        max_value=1_000_000.0,
        value=100.0,
        step=1.0,
        format="%.2f",
        help="Size of the simulated order in USD. Used for estimation only."
    )
    volatility = st.slider(
        "Volatility Estimate (%)",
        0.1,
        10.0,
        1.5,
        0.1,
        help="Estimate of short-term volatility used to approximate slippage in simulations."
    )
    fee_tier = st.selectbox(
        "Fee Tier",
        options=["Tier 1", "Tier 2", "Tier 3"],
        help="Select exchange fee tier (affects cost estimates in advanced simulation)."
    )
    st.markdown("---")
    refresh_rate = st.slider(
        "Refresh Interval (sec)",
        0.5,
        5.0,
        1.0,
        0.5,
        help="How often the dashboard polls & updates (seconds). Lower = more frequent updates but higher CPU/network usage."
    )

    # start / stop controls use session state (toggle buttons)
    if "running" not in st.session_state:
        st.session_state.running = False
    start_btn = st.button("▶ Start Live", help="Start the live websocket feed and begin real-time updates.")
    stop_btn = st.button("■ Stop Live", help="Stop the live feed and preserve the most recent snapshot.")
    st.markdown("---")
    st.header("Execution Simulation")
    simulate_order = st.checkbox("Show simulation panel", value=False, help="Toggle to show the simulation panel which uses current snapshot + volatility.")
    st.markdown("Simulation uses current orderbook snapshot and volatility to estimate fills.")

# attach client and set subscription if changed
client = get_client(URL)
# update client subscription if symbol changed
if getattr(client, "subscribe_inst", None) != symbol:
    client.subscribe_inst = symbol

def safe_rerun():
    if hasattr(st, "rerun"):
        try:
            st.rerun()
            return
        except Exception:
            pass
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
        return
    # neither API present — raise a helpful error so debugging is easy
    raise RuntimeError("Streamlit rerun API not found (tried st.rerun and st.experimental_rerun).")

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

# helper: build an interactive Altair line chart with tooltip
def make_line_chart(df, y_label):
    # df expected with Time as index
    if df.empty:
        return None
    chart_df = df.reset_index().rename(columns={df.index.name or 'index': 'Time'})
    # ensure Time column exists and is datetime
    if 'Time' in chart_df.columns:
        chart_df['Time'] = pd.to_datetime(chart_df['Time'])
    chart = (
        alt.Chart(chart_df)
        .mark_line(point=True)
        .encode(
            x=alt.X('Time:T', title='Time'),
            y=alt.Y(f'{y_label}:Q', title=y_label),
            tooltip=[alt.Tooltip('Time:T', title='Time'), alt.Tooltip(f'{y_label}:Q', title=y_label, format='.6f')]
        )
        .interactive()
    )
    return chart

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
                st.subheader("Mid Price & Spread (historic)")
                left_col, right_col = st.columns(2)
                df_mid = pd.DataFrame({"Time": list(st.session_state.times), "Mid Price": list(st.session_state.mid_prices)}).set_index("Time")
                df_spread = pd.DataFrame({"Time": list(st.session_state.times), "Spread": list(st.session_state.spreads)}).set_index("Time")

                mid_chart = make_line_chart(df_mid, 'Mid Price')
                spread_chart = make_line_chart(df_spread, 'Spread')

                with left_col:
                    st.subheader("Mid Price")
                    st.caption("Mid Price = (best_bid + best_ask) / 2 — hover for exact values and timestamps.")
                    if mid_chart:
                        st.altair_chart(mid_chart, width='stretch')
                    else:
                        st.line_chart(df_mid)

                with right_col:
                    st.subheader("Spread")
                    st.caption("Spread = best_ask - best_bid — narrow spreads generally indicate higher liquidity.")
                    if spread_chart:
                        st.altair_chart(spread_chart, width='stretch')
                    else:
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
                file_name=f"okx_orderbook_{symbol}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv",
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
            st.subheader("Mid Price & Spread (live)")
            left_col, right_col = st.columns(2)
            df_mid = pd.DataFrame({"Time": list(st.session_state.times), "Mid Price": list(st.session_state.mid_prices)}).set_index("Time")
            df_spread = pd.DataFrame({"Time": list(st.session_state.times), "Spread": list(st.session_state.spreads)}).set_index("Time")

            mid_chart = make_line_chart(df_mid, 'Mid Price')
            spread_chart = make_line_chart(df_spread, 'Spread')

            with left_col:
                st.subheader("Mid Price")
                st.caption("Interactive mid-price chart. Displays the mid price ((best_bid + best_ask)/2) with hover tooltips for precise values.")
                if mid_chart:
                    st.altair_chart(mid_chart, width='stretch')
                else:
                    st.line_chart(df_mid)

            with right_col:
                st.subheader("Spread")
                st.caption("Interactive spread chart. Lower spreads usually imply higher liquidity; hover for exact spread values.")
                if spread_chart:
                    st.altair_chart(spread_chart, width='stretch')
                else:
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
                file_name=f"okx_orderbook_{symbol}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv",
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
    # time.sleep(refresh_rate)
    # if st.session_state.running:
    #     st.experimental_rerun()
    time.sleep(refresh_rate)
    if st.session_state.running:
        safe_rerun()

except Exception as e:
    st.error(f"Error in live loop: {e}")
    try:
        client.stop()
    except Exception:
        pass
