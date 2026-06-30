import websocket
import json
from collections import deque
import time
import sqlite3
import threading  # <-- New library for concurrent workers

# We will use a Python dictionary to keep separate memory windows for each coin
asset_windows = {
    "BTC-USD": deque(maxlen=20),
    "ETH-USD": deque(maxlen=20),
    "SOL-USD": deque(maxlen=20)
}

def init_database():
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()
    # Modified table schema to include an 'asset' column
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asset_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset TEXT,
            timestamp TEXT,
            price REAL,
            rolling_avg REAL
        )
    """)
    conn.commit()
    conn.close()

def save_to_database(asset, current_price, rolling_avg):
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        INSERT INTO asset_prices (asset, timestamp, price, rolling_avg)
        VALUES (?, ?, ?, ?)
    """, (asset, current_time, current_price, rolling_avg))
    
    conn.commit()
    conn.close()

def process_market_price(asset, current_price):
    # Grab the specific memory pipe for this specific asset
    window = asset_windows[asset]
    window.append(current_price)
    rolling_avg = sum(window) / len(window)
    
    save_to_database(asset, current_price, rolling_avg)
    
    # Print out a thread-safe log message
    print(f"[{asset}] Live: ${current_price:,.2f} | 20-Tick Avg: ${rolling_avg:,.2f} | Saved to DB 💾")

def on_message(ws, message):
    data = json.loads(message)
    if "events" in data:
        for event in data["events"]:
            if "tickers" in event:
                for ticker in event["tickers"]:
                    asset = ticker.get("product_id")
                    if asset in asset_windows:  # Check if it's an asset we care about
                        price = float(ticker.get("price"))
                        process_market_price(asset, price)

def on_open(ws, asset):
    # Each worker subscribes to its own specific asset stream
    subscribe_message = {
        "type": "subscribe",
        "product_ids": [asset],
        "channel": "ticker"
    }
    ws.send(json.dumps(subscribe_message))

def start_worker(asset):
    """This function represents a single background worker thread."""
    socket_url = "wss://advanced-trade-ws.coinbase.com"
    while True:
        try:
            # We pass the specific asset name into the connection wrapper
            ws = websocket.WebSocketApp(
                socket_url, 
                on_open=lambda ws: on_open(ws, asset), 
                on_message=on_message
            )
            ws.run_forever()
        except Exception as error_msg:
            print(f"[{asset}] Stream disruption: {error_msg}. Restarting in 5s...")
            time.sleep(5)

if __name__ == "__main__":
    init_database()
    print("--- Launching Multi-Threaded Ingestion Workers ---")
    
    # Spin up an independent background thread for each asset in our list
    for crypto in asset_windows.keys():
        thread = threading.Thread(target=start_worker, args=(crypto,), daemon=True)
        thread.start()
        print(f"Worker thread initialized for {crypto}")
        time.sleep(1) # Small pause to avoid overwhelming the server connection
        
    # Keep the main script alive while background threads run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all ingestion workers gracefully.")