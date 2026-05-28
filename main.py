from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from ta.momentum import RSIIndicator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "AI Trading Backend Running"}

@app.get("/scanner")
def scanner():

    stocks = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
        "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS",
        "LT.NS", "ITC.NS"
    ]

    results = []

    for symbol in stocks:
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="5d", interval="5m")

            if data.empty:
                continue

            close = data["Close"]

            rsi = RSIIndicator(close, window=14).rsi()

            latest_price = close.iloc[-1]
            latest_rsi = rsi.iloc[-1]

            if latest_rsi > 55:
                signal = "BUY"
                confidence = 80
            elif latest_rsi < 45:
                signal = "SELL"
                confidence = 70
            else:
                signal = "HOLD"
                confidence = 50

            results.append({
                "symbol": symbol,
                "price": round(latest_price, 2),
                "RSI": round(latest_rsi, 2),
                "signal": signal,
                "entry": round(latest_price, 2),
                "target": round(latest_price * 1.02, 2),
                "stoploss": round(latest_price * 0.99, 2),
                "confidence": confidence
            })

        except:
            continue

    # ✅ ONLY BUY SIGNALS
    results = [x for x in results if x["signal"] == "BUY"]

    # sort best first
    results = sorted(results, key=lambda x: x["confidence"], reverse=True)

    return results