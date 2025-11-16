import streamlit as st
import os
import time
import pandas as pd
from dotenv import load_dotenv
from collections import deque
from datetime import datetime, timezone, timedelta
from websockets.ws_client import OrderBookClient
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

# Make Stop Live button visually red using CSS targeting aria-label.
st.markdown(
    """
    <style>
    /* Style Stop Live button by aria-label (works in current Streamlit render) */
    button[aria-label="■ Stop Live"] {
        background-color: #d9534f !important;
        color: white !important;
        border: none !important;
        height: 44px;
    }
    /* Make Start Live button more prominent */
    button[aria-label="▶ Start Live"] {
        height: 44px;
    }
    /* Narrow sidebar headings spacing */
    .css-1u3bzj6 { padding-top: 0.25rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar.expander("Quick brief — Input Parameters (click to open)", expanded=False):
    st.markdown(
        """
        **What the inputs do**
        - **Exchange / Symbol** — choose the market to subscribe to (OKX / BTC-USDT).
        - **Side / Order Type / Quantity** — used for the execution simulation only.
        - **Volatility / Fee Tier** — affect simulated slippage & costs.
        - **Refresh Interval** — how frequently the dashboard updates (seconds).
        
        **Recent UI changes**
        - Session Duration metric replaces duplicate Last update.
        - Top-of-book and Mini Trends are in the same row.
        - Orderbook tables now show cumulative qty and % of side.
        """
    )

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

    if "running" not in st.session_state:
        st.session_state.running = False

    col1, col2 = st.columns(2)

    with col1:
        start_btn = st.button(
            "▶ Start Live",
            help="Start the live websocket feed and begin real-time updates.",
            use_container_width=True  # FULL WIDTH
        )

    with col2:
        stop_btn = st.button(
            "■ Stop Live",
            help="Stop the live feed and preserve the most recent snapshot.",
            use_container_width=True,  # FULL WIDTH
        )

    st.markdown("""
        <style>
        div.stButton > button:first-child {
            height: 45px;
            font-weight: 600;
        }
        /* Stop button - second button in column (col2) */
        div[data-testid="column"]:nth-of-type(2) button {
            background-color: red !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.header("Execution Simulation")
    simulate_order = st.checkbox("Show simulation panel", value=False, help="Toggle to show the simulation panel which uses current snapshot + volatility.")
    st.markdown("Simulation uses current orderbook snapshot and volatility to estimate fills.")
    st.markdown("<div style='margin-top:10px; font-size:12px; color:gray; text-align:center;'>© 2025 All rights reserved.</div>", unsafe_allow_html=True)

# -------------------------
# Attach client & init state
# -------------------------
client = get_client(URL)
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
    raise RuntimeError("Streamlit rerun API not found (tried st.rerun and st.experimental_rerun).")

max_history = 120

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
    if "start_time" not in st.session_state:
        st.session_state.start_time = None

init_state()

# ensure ui toggle keys exist
if "ui_enh_v1" not in st.session_state:
    st.session_state.ui_enh_v1 = True
if "ui_enh_v2" not in st.session_state:
    st.session_state.ui_enh_v2 = False
if "ui_enh_v3" not in st.session_state:
    st.session_state.ui_enh_v3 = False

# handle start/stop
if start_btn:
    st.session_state.running = True
    if st.session_state.start_time is None:
        st.session_state.start_time = datetime.now(timezone.utc)
if stop_btn:
    st.session_state.running = False

# -------------------------
# Helpers and charts
# -------------------------
def check_health(latency_ms):
    if latency_ms < 100:
        return "Healthy", "✅"
    elif latency_ms < 300:
        return "Warning", "⚠️"
    else:
        return "Unhealthy", "❌"

def make_line_chart(df, y_label):
    if df.empty:
        return None
    chart_df = df.reset_index().rename(columns={df.index.name or 'index': 'Time'})
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

# formatting helpers for orderbook tables
def _format_orderbook_side(rows, side_name="bids", depth=10):
    if not rows:
        return None
    try:
        df = pd.DataFrame(rows[:depth], columns=["Price", "Qty"])
    except Exception:
        df = pd.DataFrame(rows[:depth])
        if df.shape[1] >= 2:
            df = df.iloc[:, :2]
            df.columns = ["Price", "Qty"]
        else:
            return None
    df["Price"] = df["Price"].astype(float)
    df["Qty"] = df["Qty"].astype(float)
    if side_name == "bids":
        df = df.sort_values("Price", ascending=False).reset_index(drop=True)
    else:
        df = df.sort_values("Price", ascending=True).reset_index(drop=True)
    df["CumQty"] = df["Qty"].cumsum()
    total = df["Qty"].sum()
    df["% of side"] = (df["Qty"] / total * 100).round(2) if total > 0 else 0.0
    df["Price"] = df["Price"].map(lambda x: f"{x:,.2f}")
    df["Qty"] = df["Qty"].map(lambda x: f"{x:,.6f}")
    df["CumQty"] = df["CumQty"].map(lambda x: f"{x:,.6f}")
    df["% of side"] = df["% of side"].map(lambda x: f"{x:.2f}%")
    return df

# -------------------------
# Layout placeholders
# -------------------------
st.title(f"📊 OKX {symbol} Order Book Dashboard")
top_placeholder = st.container()
chart_placeholder = st.container()
table_placeholder = st.container()
sim_placeholder = st.container()

# -------------------------
# New layout functions (only change UI rendering)
# -------------------------
def _format_duration(delta: timedelta) -> str:
    total_seconds = int(delta.total_seconds())
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"

def render_session_info_row():
    c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1])
    conn_status = "Running" if st.session_state.running else "Stopped"
    c1.metric("Connection", conn_status)
    c2.metric("Subscribed", symbol)
    if st.session_state.start_time:
        now = datetime.now(timezone.utc)
        duration = now - st.session_state.start_time
        duration_str = _format_duration(duration)
    else:
        duration_str = "0:00:00"
    c3.metric("Session Duration", duration_str)
    c4.metric("Refresh (s)", f"{refresh_rate:.1f}")
    last_health = st.session_state.health_statuses[-1] if st.session_state.health_statuses else "N/A"
    c5.metric("Health", last_health)

def render_topbook_and_mini_trends(data):
    left, right = st.columns([2,1.2])
    with left:
        st.subheader("Top-of-book")
        cols_metrics = st.columns([1,1,1,1])
        if data:
            prev_mid = st.session_state.mid_prices[-2] if len(st.session_state.mid_prices) > 1 else None
            mid_delta = (data["mid_price"] - prev_mid) if prev_mid is not None else 0.0
            cols_metrics[0].metric("Best Bid", f"{data['best_bid']:.2f}")
            cols_metrics[1].metric("Best Ask", f"{data['best_ask']:.2f}")
            cols_metrics[2].metric("Spread", f"{data['spread']:.2f}")
            cols_metrics[3].metric("Mid Price", f"{data['mid_price']:.2f}", delta=f"{mid_delta:.2f}")
        else:
            cols_metrics[0].metric("Best Bid", "N/A")
            cols_metrics[1].metric("Best Ask", "N/A")
            cols_metrics[2].metric("Spread", "N/A")
            cols_metrics[3].metric("Mid Price", "N/A")
        st.markdown("---")

        # formatted top bids/asks
        bcol, acol = st.columns(2)
        with bcol:
            st.write("Top bids (best first)")
            bids = data.get("bids", []) if isinstance(data, dict) else []
            df_bids = _format_orderbook_side(bids, side_name="bids", depth=10)
            if df_bids is None or df_bids.empty:
                # show a helpful placeholder table with zeros so it isn't blank
                placeholder = pd.DataFrame([{"Price": "-", "Qty": "-", "CumQty": "-", "% of side": "-"}])
                st.table(placeholder)
                # st.info("No bids yet.")
            else:
                st.dataframe(df_bids, width='stretch')

        with acol:
            st.write("Top asks (best first)")
            asks = data.get("asks", []) if isinstance(data, dict) else []
            df_asks = _format_orderbook_side(asks, side_name="asks", depth=10)
            if df_asks is None or df_asks.empty:
                placeholder = pd.DataFrame([{"Price": "-", "Qty": "-", "CumQty": "-", "% of side": "-"}])
                st.table(placeholder)
                # st.info("No asks yet.")
            else:
                st.dataframe(df_asks, width='stretch')

    with right:
        st.subheader("Mini Trends")
        mini_mid = pd.DataFrame({"Time": list(st.session_state.times), "Mid Price": list(st.session_state.mid_prices)}).set_index("Time")
        mini_spread = pd.DataFrame({"Time": list(st.session_state.times), "Spread": list(st.session_state.spreads)}).set_index("Time")
        st.caption("Mid Price")
        if not mini_mid.empty:
            chart_mid = make_line_chart(mini_mid.tail(60), "Mid Price")
            if chart_mid:
                st.altair_chart(chart_mid.properties(height=140), width='stretch')
            else:
                st.line_chart(mini_mid.tail(60))
        else:
            st.write("—")
        st.caption("Spread")
        if not mini_spread.empty:
            chart_sp = make_line_chart(mini_spread.tail(60), "Spread")
            if chart_sp:
                st.altair_chart(chart_sp.properties(height=120), width='stretch')
            else:
                st.line_chart(mini_spread.tail(60))
        else:
            st.write("—")

def render_help_expanders():
    st.markdown("---")
    st.subheader("Help & Field Descriptions")
    with st.expander("What is Mid Price?"):
        st.write("Mid Price = (best_bid + best_ask) / 2. Useful as a simple reference central price.")
    with st.expander("What is Spread?"):
        st.write("Spread = best_ask - best_bid. Narrow spreads typically indicate higher liquidity.")
    with st.expander("Refresh Interval"):
        st.write("Lower values update more often but increase CPU/network usage.")
    with st.expander("Simulation parameters"):
        st.write("- Volatility affects slippage estimates\n- Fee Tier affects cost calculations (not deeply implemented here)")

# -------------------------
# Render when stopped
# -------------------------
if not st.session_state.running:
    with top_placeholder:
        st.info("Live feed is stopped — press ▶ Start Live to begin real-time updates.")
        if st.session_state.last_data is None:
            st.warning("No data yet. Start live to fetch the first snapshot.")

    render_session_info_row()

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

    render_topbook_and_mini_trends(st.session_state.last_data if st.session_state.last_data else {})

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
                    est_cost = quantity
                    st.code(
                        f"Simulated Market {order_side} Order\n"
                        f"Quantity: ${quantity:.2f}\n"
                        f"Estimated Execution Price: {executed_price:.2f}\n"
                        f"Estimated Cost (USD): ${est_cost:.2f}\n"
                        f"Slippage used: {slippage:.4f}"
                    )
            else:
                st.info("Simulation will activate once data is available.")

    render_help_expanders()
    st.stop()

# -------------------------
# Main live loop
# -------------------------
try:
    data = client.get_latest_orderbook()
    latency = client.get_latency() * 1000  # ms
    now = datetime.now(timezone.utc)

    if data:
        st.session_state.last_data = data
        st.session_state.times.append(now)
        st.session_state.mid_prices.append(data.get("mid_price", 0.0))
        st.session_state.spreads.append(data.get("spread", 0.0))
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

    # Top metrics
    with top_placeholder:
        cols = st.columns([1,1,1,1])
        if data:
            prev_mid = st.session_state.mid_prices[-2] if len(st.session_state.mid_prices) > 1 else None
            mid_delta = (data.get("mid_price", 0.0) - prev_mid) if prev_mid is not None else 0.0
            cols[0].metric("Best Bid", f"{data.get('best_bid', 0.0):.2f}", delta=None)
            cols[1].metric("Best Ask", f"{data.get('best_ask', 0.0):.2f}", delta=None)
            cols[2].metric("Spread", f"{data.get('spread', 0.0):.2f}", delta=None)
            cols[3].metric("Mid Price", f"{data.get('mid_price', 0.0):.2f}", delta=f"{mid_delta:.2f}")
        else:
            st.warning("No orderbook snapshot received yet. Waiting for websocket data...")

        cols2 = st.columns([1,1,1,1])
        if data:
            cols2[0].metric("Bid Volume", f"{data.get('total_bid_volume', 0.0):.6f}")
            cols2[1].metric("Ask Volume", f"{data.get('total_ask_volume', 0.0):.6f}")
            cols2[2].metric("Latency (ms)", f"{latency:.1f}")
            cols2[3].metric("Health", st.session_state.health_statuses[-1])
        st.progress(min(1.0, len(st.session_state.times)/max_history))

    # Session info row (Session Duration replaces Last update)
    render_session_info_row()
    st.markdown("---")

    # Top-of-book + Mini Trends row
    render_topbook_and_mini_trends(st.session_state.last_data or {})

    # Original tabs preserved
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
                    if bids:
                        st.table(pd.DataFrame(bids, columns=["Price", "Qty"]))
                    else:
                        st.info("No bids yet.")
                with right:
                    st.write("Top asks (best first)")
                    asks = data.get("asks", [])[:10]
                    if asks:
                        st.table(pd.DataFrame(asks, columns=["Price", "Qty"]))
                    else:
                        st.info("No asks yet.")
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
                sdata = st.session_state.last_data
                if order_type == "Market":
                    slippage = sdata.get("mid_price", 0.0) * volatility / 100
                    executed_price = sdata.get("mid_price", 0.0) + slippage if order_side == "Buy" else sdata.get("mid_price", 0.0) - slippage
                    est_cost = quantity
                    st.info("Market order simulation (estimated)")
                    st.write(f"- Side: {order_side}")
                    st.write(f"- Quantity (USD): {quantity:.2f}")
                    st.write(f"- Estimated Execution Price: {executed_price:.2f}")
                    st.write(f"- Estimated Cost (USD): {est_cost:.2f}")
                    st.write(f"- Slippage used: {slippage:.6f}")
                else:
                    limit_price = sdata.get("best_ask") if order_side == "Buy" else sdata.get("best_bid")
                    st.info("Limit order simulation (probabilistic)")
                    st.write(f"- Side: {order_side}")
                    st.write(f"- Quantity (USD): {quantity:.2f}")
                    st.write(f"- Suggested Limit Price: {limit_price:.2f}")
                    st.write("- Note: Execution probability depends on market movement & volatility.")
            else:
                st.warning("No orderbook snapshot yet for simulation.")

    # Quick Actions (unchanged)
    if st.session_state.ui_enh_v3:
        with st.container():
            st.markdown("---")
            st.markdown("### Quick Actions")
            qa1, qa2, qa3 = st.columns(3)
            if qa1.button("Clear History"):
                st.session_state.times.clear()
                st.session_state.mid_prices.clear()
                st.session_state.spreads.clear()
                st.session_state.latencies.clear()
                st.session_state.health_statuses.clear()
                st.success("History cleared (in-memory).")
            if qa2.button("Export last 100"):
                df_export = pd.DataFrame(st.session_state.export_data[-100:])
                csv_buffer = io.StringIO()
                df_export.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="Download last 100 rows",
                    data=csv_buffer.getvalue(),
                    file_name=f"okx_orderbook_last100_{symbol}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            if qa3.button("Copy Snapshot to Clipboard (browser)"):
                if st.session_state.last_data:
                    st.text_area("Snapshot (select & copy)", value=pd.Series(st.session_state.last_data).to_json(), height=120)
                else:
                    st.warning("No snapshot to copy yet.")

    # Help expanders bottom
    render_help_expanders()

    # wait & rerun
    time.sleep(refresh_rate)
    if st.session_state.running:
        safe_rerun()

except Exception as e:
    st.error(f"Error in live loop: {e}")
    try:
        client.stop()
    except Exception:
        pass
