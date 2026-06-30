import sqlite3
import matplotlib.pyplot as plt
import time

def fetch_latest_data(asset):
    """Pulls the last 30 recorded data points for a specific asset."""
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, price, rolling_avg 
        FROM asset_prices 
        WHERE asset = ? 
        ORDER BY id DESC 
        LIMIT 30
    """, (asset,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Reverse the rows so they read from oldest to newest (left-to-right on a graph)
    rows.reverse()
    return rows

def launch_live_chart(asset="BTC-USD"):
    """Generates a constantly refreshing live chart window."""
    print(f"Opening live visualization dashboard for {asset}...")
    
    # Turn on Matplotlib's interactive live-plotting mode
    plt.ion() 
    fig, ax = plt.subplots(figsize=(10, 5))
    
    while True:
        try:
            data = fetch_latest_data(asset)
            if not data:
                print("Waiting for data rows to appear in database...")
                time.sleep(2)
                continue
                
            # Extract columns into separate clean arrays for plotting
            timestamps = [row[0].split(" ")[1] for row in data] # Just grab the HH:MM:SS part
            prices = [row[1] for row in data]
            averages = [row[2] for row in data]
            
            # Clear the old lines so the graph can update smoothly
            ax.clear()
            
            # Plot the actual live price stream vs the calculated average line
            ax.plot(timestamps, prices, label="Live Spot Price", color="blue", linewidth=2)
            ax.plot(timestamps, averages, label="20-Tick Rolling Avg", color="orange", linestyle="--")
            
            # Clean up the chart display properties
            ax.set_title(f"Real-Time Analytics Dashboard - {asset}", fontsize=14, fontweight='bold')
            ax.set_xlabel("Time (HH:MM:SS)")
            ax.set_ylabel("Price ($ USD)")
            ax.legend(loc="upper left")
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Pause briefly to draw the update to the UI window
            plt.draw()
            plt.pause(1) 
            
        except KeyboardInterrupt:
            print("\nClosing dashboard cleanly.")
            break

if __name__ == "__main__":
    # You can change this string to "ETH-USD" or "SOL-USD" to view other graphs!
    launch_live_chart("BTC-USD")