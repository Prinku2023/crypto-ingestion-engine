# High-Throughput Real-Time Data Ingestion Engine

A lightweight, fault-tolerant Python background service designed to ingest streaming market data via WebSockets, compute real-time analytics using an in-memory sliding window algorithm, and monitor price volatility.

## System Architecture
* **Ingestion Layer:** Asynchronous WebSocket client streaming low-latency ticker data directly from Coinbase Advanced Trade public feeds.
* **Processing Layer:** Utilizes an in-memory `deque` structure to achieve constant time $O(1)$ updates and moving average calculations.
* **Resiliency Layer:** Employs an automated reconnection wrapper to ensure fault tolerance during network blinks or service degradation.

## Features
* Live, sub-second streaming data processing.
* In-memory volatility tracking (flags price anomalies exceeding a 0.02% threshold from the moving average).
* Automated self-healing network logic.

## How to Run
1. Install dependencies:
   ```bash
   pip install websocket-client