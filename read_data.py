import sqlite3

def inspect_multi_asset_db():
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()
    
    # Target assets to query
    assets = ["BTC-USD", "ETH-USD", "SOL-USD"]
    
    print("\n=========================================")
    print("    DATABASE EXTRACTION REPORT           ")
    print("=========================================")
    
    for asset in assets:
        # SQL Query: Get the 3 most recent entries for each asset
        cursor.execute("""
            SELECT timestamp, price, rolling_avg 
            FROM asset_prices 
            WHERE asset = ? 
            ORDER BY id DESC 
            LIMIT 3
        """, (asset,))
        
        rows = cursor.fetchall()
        
        print(f"\n📈 Recent logs for {asset}:")
        if not rows:
            print("  No data records found yet.")
        for row in rows:
            print(f"  [{row[0]}] Price: ${row[1]:,.2f} | 20-Tick Avg: ${row[2]:,.2f}")
            
    print("=========================================")
    conn.close()

if __name__ == "__main__":
    inspect_multi_asset_db()