import streamlit as st
import sqlite3
import pandas as pd
import time

# Set up the webpage configuration
st.set_page_config(page_title="Real-Time Data Pipeline", layout="wide")
st.title("📊 Real-Time Financial Analytics Pipeline")
st.markdown("This dashboard reads live metrics directly from our concurrent SQLite data engine.")

# Create a placeholder in the UI that we can refresh dynamically
placeholder = st.empty()

def get_live_data(asset):
    """Connects to the database and pulls the latest 30 points as a DataFrame."""
    conn = sqlite3.connect("market_data.db")
    # Using pandas makes handling chart data incredibly clean
    query = """
        SELECT timestamp, price, rolling_avg 
        FROM asset_prices 
        WHERE asset = ? 
        ORDER BY id DESC 
        LIMIT 30
    """
    df = pd.read_sql_query(query, conn, params=(asset,))
    conn.close()
    
    # Reverse so time flows left-to-right on the chart
    return df.iloc[::-1]

# Run the live dashboard loop
while True:
    with placeholder.container():
        # Create three clean visual columns at the top of the webpage
        col1, col2, col3 = st.columns(3)
        
        # Pull data for all three of our active worker streams
        btc_df = get_live_data("BTC-USD")
        eth_df = get_live_data("ETH-USD")
        sol_df = get_live_data("SOL-USD")
        
        # Column 1: Bitcoin Display Card
        with col1:
            if not btc_df.empty:
                latest_btc = btc_df.iloc[-1]
                st.metric(label="🚀 BTC-USD Spot Price", value=f"${latest_btc['price']:,.2f}")
                st.line_chart(btc_df.set_index('timestamp')[['price', 'rolling_avg']])
        
        # Column 2: Ethereum Display Card
        with col2:
            if not eth_df.empty:
                latest_eth = eth_df.iloc[-1]
                st.metric(label="💎 ETH-USD Spot Price", value=f"${latest_eth['price']:,.2f}")
                st.line_chart(eth_df.set_index('timestamp')[['price', 'rolling_avg']])
                
        # Column 3: Solana Display Card
        with col3:
            if not sol_df.empty:
                latest_sol = sol_df.iloc[-1]
                st.metric(label="☀️ SOL-USD Spot Price", value=f"${latest_sol['price']:,.2f}")
                st.line_chart(sol_df.set_index('timestamp')[['price', 'rolling_avg']])
                
    # Sleep for 2 seconds before querying the SQL database again
    time.sleep(2)