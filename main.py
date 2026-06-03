from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
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

    # =========================
    # STOCK LIST
    # =========================

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
        "ITC.NS",
        "BAJFINANCE.NS",
        "TITAN.NS",
        "ASIANPAINT.NS",
        "MARUTI.NS",
        "HCLTECH.NS",
        "WIPRO.NS",
        "POWERGRID.NS",
        "ULTRACEMCO.NS",
        
        # Additional Nifty Stocks

    "ADANIPORTS.NS",
    "ADANIENT.NS",
    "BHARTIARTL.NS",
    "HINDUNILVR.NS",
    "SUNPHARMA.NS",
    "TATAMOTORS.NS",
    "TATASTEEL.NS",
    "NTPC.NS",
    "ONGC.NS",
    "COALINDIA.NS",
    "TECHM.NS",
    "INDUSINDBK.NS",
    "NESTLEIND.NS",
    "GRASIM.NS",
    "DRREDDY.NS",
    "EICHERMOT.NS",
    "CIPLA.NS",
    "HEROMOTOCO.NS",
    "JSWSTEEL.NS",
    "SHRIRAMFIN.NS",
    "TRENT.NS",
    "BAJAJFINSV.NS",
    "BPCL.NS",
    "BRITANNIA.NS",
    "DIVISLAB.NS",
    "HDFCLIFE.NS",
    "SBILIFE.NS",
    "APOLLOHOSP.NS",
    "TATACONSUM.NS",
    "BEL.NS",
    "PIDILITIND.NS",
    "DLF.NS"
]

    results = []
    # =========================
    # MARKET HOURS FILTER
    # =========================

    now = datetime.now()

    market_open = (
        (now.hour > 9 or (now.hour == 9 and now.minute >= 15))
        and
        (now.hour < 15 or (now.hour == 15 and now.minute <= 30))
    )

    if not market_open:
        return []
    # =========================
    # NIFTY TREND FILTER
    # =========================

    nifty = yf.Ticker("^NSEI")

    nifty_data = nifty.history(
        period="5d",
        interval="15m"
    )

    nifty_close = nifty_data["Close"]

    nifty_ema20 = nifty_close.ewm(
        span=20,
        adjust=False
    ).mean()

    latest_nifty = nifty_close.iloc[-1]

    latest_nifty_ema20 = nifty_ema20.iloc[-1]

    market_bullish = latest_nifty > latest_nifty_ema20

    # =========================
    # STOCK SCANNING
    # =========================

    for symbol in stocks:

        try:

            stock = yf.Ticker(symbol)

            # =========================
            # 5-MINUTE DATA
            # =========================

            data = stock.history(
                period="5d",
                interval="5m"
            )

            # =========================
            # 15-MINUTE DATA
            # =========================

            data_15m = stock.history(
                period="5d",
                interval="15m"
            )

            if data.empty or data_15m.empty:
                continue

            # =========================
            # RSI
            # =========================

            close = data["Close"]

            rsi = RSIIndicator(
                close,
                window=14
            ).rsi()

            # =========================
            # VWAP
            # =========================

            data["VWAP"] = (
                (data["Close"] * data["Volume"]).cumsum()
                / data["Volume"].cumsum()
            )

            # =========================
            # 5M EMA
            # =========================

            data["EMA9"] = data["Close"].ewm(
                span=9,
                adjust=False
            ).mean()

            data["EMA20"] = data["Close"].ewm(
                span=20,
                adjust=False
            ).mean()

            # =========================
            # 15M EMA
            # =========================

            data_15m["EMA9"] = data_15m["Close"].ewm(
                span=9,
                adjust=False
            ).mean()

            data_15m["EMA20"] = data_15m["Close"].ewm(
                span=20,
                adjust=False
            ).mean()

            # =========================
            # VOLUME
            # =========================

            data["AvgVolume"] = data["Volume"].rolling(20).mean()

            # =========================
            # ATR
            # =========================

            atr_indicator = AverageTrueRange(
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                window=14
            )

            data["ATR"] = atr_indicator.average_true_range()

            # =========================
            # LATEST VALUES
            # =========================

            latest_price = close.iloc[-1]

            latest_rsi = rsi.iloc[-1]

            latest_vwap = data["VWAP"].iloc[-1]

            latest_ema9 = data["EMA9"].iloc[-1]

            latest_ema20 = data["EMA20"].iloc[-1]

            latest_ema9_15m = data_15m["EMA9"].iloc[-1]

            latest_ema20_15m = data_15m["EMA20"].iloc[-1]

            latest_volume = data["Volume"].iloc[-1]

            avg_volume = data["AvgVolume"].iloc[-1]

            latest_atr = data["ATR"].iloc[-1]

            # =========================
            # CONDITIONS
            # =========================

            price_above_vwap = latest_price > latest_vwap

            ema_bullish_5m = latest_ema9 > latest_ema20

            ema_bullish_15m = (
                latest_ema9_15m > latest_ema20_15m
            )

            multi_timeframe_bullish = (
                ema_bullish_5m
                and ema_bullish_15m
            )

            volume_boost = (
                latest_volume > (avg_volume * 1.0)
            )

            # =========================
            # SCORING SYSTEM
            # =========================

            score = 0

            # RSI
            if latest_rsi > 50:
                score += 1

            # VWAP
            if price_above_vwap:
                score += 2

            # MULTI-TIMEFRAME
            if multi_timeframe_bullish:
                score += 3

            # VOLUME
            if volume_boost:
                score += 1

            # MARKET TREND
            if market_bullish:
                score += 2

            # =========================
            # SIGNAL LOGIC
            # =========================

            if score >= 7:
                signal = "BUY"

            elif score >= 4:
                signal = "HOLD"

            else:
                signal = "SELL"

            # =========================
            # CONFIDENCE
            # =========================

            confidence = round((score / 9) * 100, 2)

            # =========================
            # ONLY BUY SIGNALS
            # =========================

            if signal == "BUY":

                results.append({

                    "symbol": symbol,

                    "price": round(latest_price, 2),

                    "RSI": round(latest_rsi, 2),

                    "VWAP": round(latest_vwap, 2),

                    "EMA9_5M": round(latest_ema9, 2),

                    "EMA20_5M": round(latest_ema20, 2),

                    "EMA9_15M": round(latest_ema9_15m, 2),

                    "EMA20_15M": round(latest_ema20_15m, 2),

                    "signal": signal,

                    "entry": round(latest_price, 2),

                    "target": round(latest_price + (2 * latest_atr), 2),

                    "stoploss": round(latest_price - latest_atr, 2),

                    "confidence": confidence,

                    "score": score,

                    "market_trend": (
                        "Bullish"
                        if market_bullish
                        else "Bearish"
                    )
                })

        except Exception as e:

            print(f"Error in {symbol}: {e}")

            continue

    # =========================
    # SORT BEST SIGNALS
    # =========================

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    results = results[:5]

    return results