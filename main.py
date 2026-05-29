from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from ta.momentum import RSIIndicator
import numpy as np

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
    return {"message": "Advanced AI Trading Backend Running"}

@app.get("/scanner")
def scanner():

    stocks = [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "SBIN.NS",
        "AXISBANK.NS",
        "KOTAKBANK.NS",
        "LT.NS",
        "ITC.NS"
    ]

    results = []

    for symbol in stocks:

        try:
            stock = yf.Ticker(symbol)

            data = stock.history(period="5d", interval="5m")

            if data.empty:
                continue

            # CLOSE PRICE
            close = data["Close"]

            # RSI
            rsi = RSIIndicator(close, window=14).rsi()

            # VWAP
            data["VWAP"] = (
                (data["Close"] * data["Volume"]).cumsum()
                / data["Volume"].cumsum()
            )

            # EMA
            data["EMA9"] = data["Close"].ewm(span=9, adjust=False).mean()
            data["EMA20"] = data["Close"].ewm(span=20, adjust=False).mean()

            # AVERAGE VOLUME
            data["AvgVolume"] = data["Volume"].rolling(20).mean()

            # LATEST VALUES
            latest_price = close.iloc[-1]
            latest_rsi = rsi.iloc[-1]

            latest_vwap = data["VWAP"].iloc[-1]

            latest_ema9 = data["EMA9"].iloc[-1]
            latest_ema20 = data["EMA20"].iloc[-1]

            latest_volume = data["Volume"].iloc[-1]
            avg_volume = data["AvgVolume"].iloc[-1]

            # CONDITIONS
            price_above_vwap = latest_price > latest_vwap

            ema_bullish = latest_ema9 > latest_ema20

            volume_boost = latest_volume > (avg_volume * 1.5)

            # SCORING SYSTEM
            score = 0

            if latest_rsi > 55:
                score += 1

            if price_above_vwap:
                score += 2

            if ema_bullish:
                score += 2

            if volume_boost:
                score += 2

            # SIGNAL DECISION
            if score >= 4:
                signal = "BUY"
            elif score >= 3:
                signal = "HOLD"
            else:
                signal = "SELL"

            # DYNAMIC CONFIDENCE
            confidence = round((score / 7) * 100, 2)

            # ONLY GOOD BUY SIGNALS
            if signal == "BUY":

                results.append({
                    "symbol": symbol,

                    "price": round(latest_price, 2),

                    "RSI": round(latest_rsi, 2),

                    "VWAP": round(latest_vwap, 2),

                    "EMA9": round(latest_ema9, 2),

                    "EMA20": round(latest_ema20, 2),

                    "signal": signal,

                    "entry": round(latest_price, 2),

                    "target": round(latest_price * 1.02, 2),

                    "stoploss": round(latest_price * 0.99, 2),

                    "confidence": confidence
                })

        except Exception as e:
            print(f"Error in {symbol}: {e}")
            continue

    # SORT BEST SIGNALS FIRST
    results = sorted(
        results,
        key=lambda x: x["confidence"],
        reverse=True
    )

    return results