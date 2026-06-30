import websocket
import json
from collections import deque
import time

price_window = deque(maxlen=20)

def process_market_price(current_price):
    price_window.append(current_price)
    rolling_avg = sum(price_window) / len(price_window)
    
    # Clean output print for the cloud environment
    print("-----------------------------------------")
    print(f"Live BTC Price:      ${current_price:,.2f}")
    print(f"20-Tick Moving Avg:  ${rolling_avg:,.2f}")
    print(f"Data Capacity in RAM: {len(price_window)}/20")
    
    if len(price_window) == 20:
        anomaly_threshold = rolling_avg * 0.0002 
        if abs(current_price - rolling_avg) > anomaly_threshold:
            print("⚠️  ANOMALY ALERT: Volatility spike detected!")
    print("-----------------------------------------")

def on_message(ws, message):
    data = json.loads(message)
    if "events" in data:
        for event in data["events"]:
            if "tickers" in event:
                for ticker in event["tickers"]:
                    if ticker.get("product_id") == "BTC-USD":
                        price = float(ticker.get("price"))
                        process_market_price(price)

def on_open(ws):
    subscribe_message = {
        "type": "subscribe",
        "product_ids": ["BTC-USD"],
        "channel": "ticker"
    }
    ws.send(json.dumps(subscribe_message))

if __name__ == "__main__":
    socket_url = "wss://advanced-trade-ws.coinbase.com"
    # Run a single clean connection pass for cloud demonstration
    ws = websocket.WebSocketApp(socket_url, on_open=on_open, on_message=on_message)
    ws.run_forever()