import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
# from NorenApi import NorenApi  # Shoonya official API library

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Shoonya API credentials (अपनी डिटेल्स भरें)
USER_ID = "YOUR_USER_ID"
PASSWORD = "YOUR_PASSWORD"
TWO_FA = "YOUR_DOB_OR_PAN"  # YYYYMMDD or PAN
VENDOR_CODE = "YOUR_VENDOR_CODE"
API_KEY = "YOUR_API_KEY"
IMEI = "1234567890abcdef"

# class ShoonyaApiPy(NorenApi):
#     def __init__(self):
#         super().__init__(remotepath='https://api.shoonya.com/NorenWClientTP/')

# shoonya_client = ShoonyaApiPy()

@app.route('/')
def serve_dashboard():
    return send_from_directory('.', 'dashboard.html')

@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    index = request.args.get('index', 'NIFTY')
    expiry = request.args.get('expiry', '')
    
    # यहाँ Shoonya API से लाइव इंडेक्स स्पॉट और ऑप्शन चेन फैच करने का लॉजिक आएगा।
    # अभी टेस्टिंग/डिस्प्ले स्ट्रक्चर का फॉर्मेट नीचे दिया गया है:
    
    mock_data = {
        "index": index,
        "timestamp": "2026-09-13T09:35:00+05:30",
        "spot": 25100 if index == "NIFTY" else (51200 if index == "BANKNIFTY" else 82000),
        "expiries": ["2026-09-17", "2026-09-24"],
        "chain": [
            {
                "strike": 25100,
                "expiry": "2026-09-17",
                "CE": {"ltp": 125.5, "oi": 500000, "chgOi": 25000, "volume": 120000, "iv": 14.5, "bid": 125.0, "ask": 126.0, "delta": 0.55, "gamma": 0.0025, "theta": -12.4, "vega": 15.2},
                "PE": {"ltp": 115.0, "oi": 480000, "chgOi": -10000, "volume": 110000, "iv": 15.0, "bid": 114.5, "ask": 115.5, "delta": -0.45, "gamma": 0.0025, "theta": -11.8, "vega": 14.8}
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
  
