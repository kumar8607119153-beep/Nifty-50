import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS


# --------------------------------------------------
# Flask App
# --------------------------------------------------

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)


# --------------------------------------------------
# Shoonya Configuration
# Keep credentials in Render Environment Variables.
# --------------------------------------------------

USER_ID = os.getenv("SHOONYA_USER_ID", "")
PASSWORD = os.getenv("SHOONYA_PASSWORD", "")
TWO_FA = os.getenv("SHOONYA_TWO_FA", "")
VENDOR_CODE = os.getenv("SHOONYA_VENDOR_CODE", "")
API_KEY = os.getenv("SHOONYA_API_KEY", "")
IMEI = os.getenv("SHOONYA_IMEI", "1234567890abcdef")


# --------------------------------------------------
# Home / Dashboard
# --------------------------------------------------

@app.route("/")
def serve_dashboard():
    dashboard_path = os.path.join(app.root_path, "dashboard.html")

    if os.path.exists(dashboard_path):
        return send_from_directory(app.root_path, "dashboard.html")

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>Flask Server is Running</h1>
        <p>dashboard.html file was not found.</p>
        <p>Please upload dashboard.html in the same folder as app.py.</p>
    </body>
    </html>
    """, 404


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Trading dashboard server is running"
    })


# --------------------------------------------------
# Market Data
# --------------------------------------------------

@app.route("/api/market-data", methods=["GET"])
def get_market_data():

    index = request.args.get("index", "NIFTY").upper()
    expiry = request.args.get("expiry", "")

    if index == "BANKNIFTY":
        spot = 51200
    elif index == "FINNIFTY":
        spot = 23800
    elif index == "SENSEX":
        spot = 82000
    else:
        index = "NIFTY"
        spot = 25100

    # --------------------------------------------------
    # TEST / MOCK DATA
    # Replace this later with live Shoonya data.
    # --------------------------------------------------

    mock_data = {
        "success": True,
        "mode": "mock",
        "index": index,
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "spot": spot,

        "selectedExpiry": expiry,

        "expiries": [
            "2026-09-17",
            "2026-09-24"
        ],

        "chain": [
            {
                "strike": 25100,
                "expiry": "2026-09-17",

                "CE": {
                    "ltp": 125.50,
                    "oi": 500000,
                    "chgOi": 25000,
                    "volume": 120000,
                    "iv": 14.50,
                    "bid": 125.00,
                    "ask": 126.00,
                    "delta": 0.55,
                    "gamma": 0.0025,
                    "theta": -12.40,
                    "vega": 15.20
                },

                "PE": {
                    "ltp": 115.00,
                    "oi": 480000,
                    "chgOi": -10000,
                    "volume": 110000,
                    "iv": 15.00,
                    "bid": 114.50,
                    "ask": 115.50,
                    "delta": -0.45,
                    "gamma": 0.0025,
                    "theta": -11.80,
                    "vega": 14.80
                }
            }
        ],

        "indicators": {
            "supertrend": "Bullish",
            "vwap": 25080,
            "rsi": 58.4,
            "macd": 12.5,
            "adx": 24.1,
            "atr": 45.2
        },

        "context": {
            "vix": 13.8,
            "gift": 25120,
            "usdinr": 84.15,
            "globalRisk": "Neutral"
        },

        "news": []
    }

    return jsonify(mock_data)


# --------------------------------------------------
# API Status
# --------------------------------------------------

@app.route("/api/status", methods=["GET"])
def api_status():

    return jsonify({
        "server": "online",
        "shoonya_configured": bool(
            USER_ID and PASSWORD and VENDOR_CODE and API_KEY
        ),
        "data_mode": "mock"
    })


# --------------------------------------------------
# 404 Handler
# --------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({
        "success": False,
        "error": "Not Found",
        "message": "The requested URL was not found on the server."
    }), 404


# --------------------------------------------------
# Run Locally
# --------------------------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
)
