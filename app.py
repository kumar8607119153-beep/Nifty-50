import os
import json
import requests
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)


# ============================================================
# FLATTRADE CONFIGURATION
# ============================================================
# GitHub / Render Environment Variables में डालें:
#
# FLATTRADE_USER_ID
# FLATTRADE_API_KEY
# FLATTRADE_API_SECRET
# FLATTRADE_ACCESS_TOKEN
#
# API Secret इस file में कभी सीधे न लिखें.
# ============================================================

FLATTRADE_USER_ID = os.getenv(
    "FLATTRADE_USER_ID", ""
).strip()

FLATTRADE_API_KEY = os.getenv(
    "FLATTRADE_API_KEY", ""
).strip()

FLATTRADE_API_SECRET = os.getenv(
    "FLATTRADE_API_SECRET", ""
).strip()

FLATTRADE_ACCESS_TOKEN = os.getenv(
    "FLATTRADE_ACCESS_TOKEN", ""
).strip()


# FlatTrade API v2
BASE_URL = (
    "https://piconnect.flattrade.in/PiConnectAPI"
)


# ============================================================
# FLATTRADE REQUEST
# ============================================================

def flattrade_request(endpoint, data=None):

    if not FLATTRADE_USER_ID:
        return {
            "stat": "Not_Ok",
            "emsg": "FLATTRADE_USER_ID missing"
        }

    if not FLATTRADE_ACCESS_TOKEN:
        return {
            "stat": "Not_Ok",
            "emsg": "FLATTRADE_ACCESS_TOKEN missing"
        }

    if data is None:
        data = {}

    payload = {
        "uid": FLATTRADE_USER_ID,
        **data
    }

    try:

        response = requests.post(
            f"{BASE_URL}/{endpoint}",
            data={
                "jData": json.dumps(payload),
                "jKey": FLATTRADE_ACCESS_TOKEN
            },
            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:

        return {
            "stat": "Not_Ok",
            "emsg": str(e)
        }

    except ValueError:

        return {
            "stat": "Not_Ok",
            "emsg":
                "FlatTrade returned invalid response"
        }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    dashboard_path = os.path.join(
        app.root_path,
        "dashboard.html"
    )

    if os.path.exists(dashboard_path):

        return send_from_directory(
            app.root_path,
            "dashboard.html"
        )

    return jsonify({
        "status": "online",
        "broker": "FlatTrade",
        "message":
            "Backend is running. dashboard.html is separate."
    })


# ============================================================
# HEALTH
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "broker": "FlatTrade",
        "server": "online"
    })


# ============================================================
# API STATUS
# ============================================================

@app.route("/api/status")
def api_status():

    result = {

        "server": "online",

        "broker": "FlatTrade",

        "api_key_present":
            bool(FLATTRADE_API_KEY),

        "api_secret_present":
            bool(FLATTRADE_API_SECRET),

        "user_id_present":
            bool(FLATTRADE_USER_ID),

        "access_token_present":
            bool(FLATTRADE_ACCESS_TOKEN),

        "data_mode":
            "live"
            if (
                FLATTRADE_USER_ID
                and FLATTRADE_API_KEY
                and FLATTRADE_API_SECRET
                and FLATTRADE_ACCESS_TOKEN
            )
            else "not_configured"
    }


    # --------------------------------------------------------
    # FlatTrade session test
    # --------------------------------------------------------

    if FLATTRADE_ACCESS_TOKEN:

        response = flattrade_request(
            "UserDetails"
        )

        if response.get("stat") == "Ok":

            result["flattrade_connection"] = "connected"

        else:

            result["flattrade_connection"] = "error"

            result["error"] = response.get(
                "emsg",
                "Authentication failed"
            )

    else:

        result["flattrade_connection"] = (
            "not_configured"
        )


    return jsonify(result)


# ============================================================
# USER DETAILS
# ============================================================

@app.route("/api/user-details")
def user_details():

    return jsonify(
        flattrade_request(
            "UserDetails"
        )
    )


# ============================================================
# SEARCH SCRIP
# ============================================================

@app.route("/api/search")
def search_scrip():

    text = request.args.get(
        "text",
        "NIFTY"
    ).strip()

    exchange = request.args.get(
        "exchange",
        "NSE"
    ).upper()


    result = flattrade_request(
        "SearchScrip",
        {
            "exch": exchange,
            "stext": text
        }
    )

    return jsonify(result)


# ============================================================
# INDEX LIST
# ============================================================

@app.route("/api/index-list")
def index_list():

    exchange = request.args.get(
        "exchange",
        "NSE"
    ).upper()


    result = flattrade_request(
        "GetIndexList",
        {
            "exch": exchange
        }
    )

    return jsonify(result)


# ============================================================
# QUOTE
# ============================================================
# Display code किसी symbol/token का LTP मांग सकता है.
#
# Example:
# /api/quote?exchange=NSE&token=26000
# ============================================================

@app.route("/api/quote")
def quote():

    exchange = request.args.get(
        "exchange",
        "NSE"
    ).upper()

    token = request.args.get(
        "token",
        ""
    ).strip()


    if not token:

        return jsonify({
            "success": False,
            "error": "token is required"
        }), 400


    result = flattrade_request(
        "Touchline",
        {
            "exch": exchange,
            "token": token
        }
    )

    return jsonify(result)


# ============================================================
# 5-MINUTE CANDLES
# ============================================================

@app.route("/api/candles")
def candles():

    exchange = request.args.get(
        "exchange",
        "NSE"
    ).upper()

    token = request.args.get(
        "token",
        ""
    ).strip()

    interval = request.args.get(
        "interval",
        "5"
    ).strip()


    if not token:

        return jsonify({
            "success": False,
            "error": "token is required"
        }), 400


    now = int(
        datetime.now(
            timezone.utc
        ).timestamp()
    )

    start = now - (
        7 * 24 * 60 * 60
    )


    result = flattrade_request(
        "TPSeries",
        {
            "exch": exchange,
            "token": token,
            "st": str(start),
            "et": str(now),
            "intrv": interval
        }
    )

    return jsonify(result)


# ============================================================
# MARKET DATA
# ============================================================
# NIFTY 50
# NIFTY BANK
# SENSEX
#
# तीनों को अलग-अलग handle किया गया है.
# ============================================================

@app.route("/api/market-data")
def market_data():

    index = request.args.get(
        "index",
        "NIFTY"
    ).upper()

    expiry = request.args.get(
        "expiry",
        ""
    )


    allowed = {
        "NIFTY": "NIFTY",
        "BANKNIFTY": "BANKNIFTY",
        "SENSEX": "SENSEX"
    }


    if index not in allowed:

        return jsonify({
            "success": False,
            "error":
                "Supported indexes: NIFTY, BANKNIFTY, SENSEX"
        }), 400


    # --------------------------------------------------------
    # FlatTrade index exchange
    # --------------------------------------------------------

    exchange = (
        "BSE"
        if index == "SENSEX"
        else "NSE"
    )


    # --------------------------------------------------------
    # Get index list
    # --------------------------------------------------------

    index_response = flattrade_request(
        "GetIndexList",
        {
            "exch": exchange
        }
    )


    if index_response.get("stat") != "Ok":

        return jsonify({

            "success": False,

            "mode": "live",

            "broker": "FlatTrade",

            "index": index,

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "error":
                index_response.get(
                    "emsg",
                    "Unable to get index list"
                )
        })


    values = index_response.get(
        "values",
        []
    )


    # --------------------------------------------------------
    # Find selected index
    # --------------------------------------------------------

    aliases = {

        "NIFTY": [
            "NIFTY 50",
            "NIFTY"
        ],

        "BANKNIFTY": [
            "NIFTY BANK",
            "BANK NIFTY",
            "NIFTYBANK"
        ],

        "SENSEX": [
            "SENSEX",
            "BSE SENSEX"
        ]
    }


    selected = None


    for item in values:

        name = str(
            item.get(
                "idxname",
                ""
            )
        ).upper().strip()


        if name in [
            x.upper()
            for x in aliases[index]
        ]:

            selected = item
            break


    if selected is None:

        return jsonify({

            "success": False,

            "mode": "live",

            "broker": "FlatTrade",

            "index": index,

            "error":
                f"{index} not found in FlatTrade index list",

            "available_indexes": values
        })


    token = str(
        selected.get(
            "token",
            ""
        )
    )


    # --------------------------------------------------------
    # Get 5-minute candles
    # --------------------------------------------------------

    now = int(
        datetime.now(
            timezone.utc
        ).timestamp()
    )

    start = now - (
        7 * 24 * 60 * 60
    )


    candle_response = flattrade_request(
        "TPSeries",
        {
            "exch": exchange,
            "token": token,
            "st": str(start),
            "et": str(now),
            "intrv": "5"
        }
    )


    # --------------------------------------------------------
    # Extract candle list
    # --------------------------------------------------------

    if isinstance(
        candle_response,
        list
    ):

        candle_values = candle_response

    else:

        candle_values = candle_response.get(
            "values",
            []
        )


    # --------------------------------------------------------
    # Latest LTP from candle
    # --------------------------------------------------------

    spot = None


    if candle_values:

        latest = candle_values[-1]

        value = (
            latest.get("intc")
            or latest.get("lp")
            or latest.get("close")
        )


        try:

            spot = float(value)

        except (
            TypeError,
            ValueError
        ):

            spot = None


    # --------------------------------------------------------
    # Frontend-compatible response
    # --------------------------------------------------------

    return jsonify({

        "success": True,

        "mode": "live",

        "broker": "FlatTrade",

        "index": index,

        "token": token,

        "exchange": exchange,

        "timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "spot": spot,

        "selectedExpiry": expiry,

        "expiries": [],

        "chain": [],

        "candles": candle_values,

        "indicators": {},

        "context": {},

        "news": []
    })


# ============================================================
# OPTION CHAIN
# ============================================================

@app.route("/api/option-chain")
def option_chain():

    exchange = request.args.get(
        "exchange",
        "NFO"
    ).upper()

    symbol = request.args.get(
        "symbol",
        ""
    ).strip()

    strike = request.args.get(
        "strike",
        ""
    ).strip()

    count = request.args.get(
        "count",
        "5"
    ).strip()


    if not symbol:

        return jsonify({
            "success": False,
            "error": "symbol is required"
        }), 400


    if not strike:

        return jsonify({
            "success": False,
            "error": "strike is required"
        }), 400


    result = flattrade_request(
        "GetOptionChain",
        {
            "exch": exchange,
            "tsym": symbol,
            "strprc": strike,
            "cnt": count
        }
    )

    return jsonify(result)


# ============================================================
# ERROR HANDLER
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "success": False,

        "error": "Not Found",

        "message":
            "Requested URL does not exist."
    }), 404


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
)
