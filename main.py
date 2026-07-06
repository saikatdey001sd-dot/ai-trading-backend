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

    print("SCANNER CALLED")

    print(">>> SCANNER FUNCTION STARTED <<<")

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
    "TMCV.NS",
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
    "DLF.NS",   
    "ABB.NS",
    "ACC.NS",
    "AMBUJACEM.NS",
    "AUBANK.NS",
    "BANDHANBNK.NS",
    "BHEL.NS",
    "CANBK.NS",
    "CGPOWER.NS",
    "CHOLAFIN.NS",
    "CUMMINSIND.NS",
    "DABUR.NS",
    "DMART.NS",
    "GAIL.NS",
    "GODREJCP.NS",
    "HAL.NS",
    "HAVELLS.NS",
    "ICICIPRULI.NS",
    "IDFCFIRSTB.NS",
    "INDUSTOWER.NS",
    "IOC.NS",
    "IRCTC.NS",
    "JINDALSTEL.NS",
    "LICHSGFIN.NS",
    "LODHA.NS",
    "LUPIN.NS",
    "MOTHERSON.NS",
    "NAUKRI.NS",
    "NMDC.NS",
    "OBEROIRLTY.NS",
    "OFSS.NS",
    "PAGEIND.NS",
    "PFC.NS",
    "PNB.NS",
    "POLYCAB.NS",
    "RECLTD.NS",
    "SAIL.NS",
    "SHREECEM.NS",
    "SIEMENS.NS",
    "SRF.NS",
    "TATAPOWER.NS",
    "TORNTPHARM.NS",
    "TORNTPOWER.NS",
    "TVSMOTOR.NS",
    "UNIONBANK.NS",
    "VBL.NS",
    "VEDL.NS",
    "ZYDUSLIFE.NS"
]

    results = []
    # =========================
    # MARKET HOURS FILTER
    # =========================

    from datetime import datetime
    import pytz

    india = pytz.timezone("Asia/Kolkata")
    now = datetime.now(india)

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

    nifty_ema9 = nifty_close.ewm(
        span=9,
        adjust=False
    ).mean()

    latest_nifty_ema9 = nifty_ema9.iloc[-1]

    print("\n===== NIFTY =====")
    print("Latest Nifty :", round(latest_nifty, 2))
    print("EMA9         :", round(latest_nifty_ema9, 2))
    print("EMA20        :", round(latest_nifty_ema20, 2))
    print("=================\n")

    print(nifty_data.tail(5))

    market_bullish = latest_nifty_ema9 > latest_nifty_ema20

    print("Market Bullish =", market_bullish)
    
    print("\n========================")
    print("NIFTY STATUS")
    print("========================")
    print(f"Latest Nifty : {latest_nifty:.2f}")
    print(f"EMA9         : {latest_nifty_ema9:.2f}")
    print(f"EMA20        : {latest_nifty_ema20:.2f}")
    print(f"Market Bullish : {market_bullish}")
    print("========================\n")

    # =========================
    # STOCK SCANNING    
    # =========================

    total_stocks = 0

    rsi_pass = 0
    vwap_pass = 0
    ema5_pass = 0
    ema15_pass = 0
    volume_pass = 0
    market_pass = 0
    buy_candidates = 0


    for symbol in stocks:

        print(f"Checking {symbol}...")

        try:
        
            total_stocks += 1

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

            # Typical Price
            typical_price = (
                data["High"] +
                data["Low"] +
                data["Close"]
            ) / 3

            # VWAP
            data["VWAP"] = (
                (typical_price * data["Volume"]).cumsum()
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

            avg_volume = data["Volume"].rolling(20).mean().iloc[-1]

            volume_ratio = (
                latest_volume / avg_volume
                if avg_volume > 0
                else 0
            )

            latest_atr = data["ATR"].iloc[-1]

            # =========================
            # SUPPORT & RESISTANCE
            # =========================

            recent_high = data_15m["High"].tail(20).max()
            recent_low = data_15m["Low"].tail(20).min()

            # Highest high of last 5 completed candles

            breakout_level = data["High"].iloc[-6:-1].max()

            # Current candle close

            current_close = data["Close"].iloc[-1]

            # Breakout confirmation

            breakout_confirmed = (
                current_close > breakout_level
                and volume_ratio >= 1.3
            )

            distance_to_resistance = ((recent_high - latest_price) / latest_price) * 100
            distance_from_support = ((latest_price - recent_low) / latest_price) * 100

            # =========================
            # CONDITIONS
            # =========================

            price_above_vwap = latest_price > (latest_vwap * 1.003)

            ema_bullish_5m = (
                latest_ema9 > latest_ema20
            )

            ema_bullish_15m = (
                latest_ema9_15m > latest_ema20_15m
            )

            multi_timeframe_bullish = (
                ema_bullish_5m
                and ema_bullish_15m
            )

            volume_boost = (
                latest_volume > (avg_volume * 1.5)
            )

            # =========================
            # SCORING SYSTEM
            # =========================

            score = 0

            # RSI
            if 60 <= latest_rsi < 65:
               score += 1
               rsi_pass += 1
            elif 65 <= latest_rsi < 72:
               score += 2
               rsi_pass += 1
            elif latest_rsi >= 72:
               score += 1
               rsi_pass += 1

            # VWAP
            if price_above_vwap:
                score += 2
                vwap_pass += 1

            # MULTI-TIMEFRAME
            if multi_timeframe_bullish:
                score += 3

            if ema_bullish_5m:
                ema5_pass += 1

            if ema_bullish_15m:
                ema15_pass += 1

            # VOLUME
            if volume_boost:
                score += 1
                volume_pass += 1

            # MARKET TREND
            if market_bullish:
                score += 2
                market_pass += 1
            print(
                symbol,
                "MARKET=", market_bullish,
                "RSI=", round(latest_rsi, 2),
                "VWAP=", price_above_vwap,
                "5M=", ema_bullish_5m,
                "15M=", ema_bullish_15m,
                "VOL=", volume_boost,
                "SCORE=", score
            )

            # =========================
            # CONFIDENCE
            # =========================

            confidence = 40

            # Market trend
            if market_bullish:
               confidence += 10

            # RSI contribution
            if 60 <= latest_rsi <= 64:
               confidence += 12
            elif 64 < latest_rsi <= 68:
               confidence += 8
            elif 58 <= latest_rsi < 60:
               confidence += 5

            # VWAP strength
            vwap_gap = ((latest_price - latest_vwap) / latest_vwap) * 100

            if vwap_gap >= 2:
                confidence += 12
            elif vwap_gap >= 1:
                confidence += 8
            elif vwap_gap >= 0.5:
                confidence += 4

            # EMA strength
            ema_gap_5m = (
                (latest_ema9 - latest_ema20)
                / latest_ema20
            ) * 100

            ema_gap_15m = (
                (latest_ema9_15m - latest_ema20_15m)
                / latest_ema20_15m
            ) * 100

            strong_ema = (
                ema_gap_5m >= 0.25
                and ema_gap_15m >= 0.25
            )

            if ema_gap_5m >= 0.50:
                confidence += 8
            elif ema_gap_5m >= 0.25:
                confidence += 5

            if ema_gap_15m >= 0.50:
                confidence += 8
            elif ema_gap_15m >= 0.25:
                confidence += 5

            if volume_ratio >= 2:
                confidence += 15
            elif volume_ratio >= 1.5:
                confidence += 10
            elif volume_ratio >= 1.2:
                confidence += 5

            confidence = max(40, min(round(confidence, 1), 95))

            # =========================
            # SIGNAL LOGIC
            # =========================

            if market_bullish:
                required_score = 6
                required_rsi = 50
            else:
                required_score = 8
                required_rsi = 60

            if (
                score >= required_score
                and latest_rsi >= required_rsi
                and confidence >= 75
                and strong_ema
                and breakout_confirmed
            ):
                signal = "BUY"

            elif score >= 4:
                signal = "HOLD"

            else:
                signal = "SELL"

            # =========================
            # RESISTANCE FILTER
            # =========================

            if signal == "BUY" and distance_to_resistance < 1.5:
                signal = "HOLD"

            
            # =========================
            # ONLY BUY SIGNALS
            # =========================


            if signal == "BUY":
                
                print(
                    symbol,
                    "CONF=", confidence,
                    "RSI=", round(latest_rsi, 2),
                    "VWAP GAP=", round(vwap_gap, 2),
                    "EMA5 GAP=", round(ema_gap_5m, 2),
                    "EMA15 GAP=", round(ema_gap_15m, 2),
                    "SUP=", round(recent_low, 2),
                    "RES=", round(recent_high, 2),
                    "DIST RES=", round(distance_to_resistance, 2),
                    "DIST SUP=", round(distance_from_support, 2)
                )

                entry_price = round(
                    data["High"].iloc[-1] + (0.20 * latest_atr),
                    2
                )

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

                    "entry": entry_price,

                    "target": round(entry_price + (2 * latest_atr), 2),

                    "stoploss": round(entry_price - latest_atr, 2),

                    "confidence": confidence,

                    "support": round(recent_low, 2),

                    "resistance": round(recent_high, 2),

                    "distance_to_resistance": round(distance_to_resistance, 2),

                    "distance_from_support": round(distance_from_support, 2),

                    "volume_ratio": round(volume_ratio, 2),

                    "vwap_gap": round(vwap_gap, 2),

                    "ema_gap_5m": round(ema_gap_5m, 2),

                    "ema_gap_15m": round(ema_gap_15m, 2),

                    "score": score,

                    "market_trend": (
                        "Bullish"
                        if market_bullish
                        else "weak"
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

    results = results[:3]
    
    # =========================
    # DIAGNOSTICS SUMMARY
    # =========================

    print("Reached diagnostics")

    print("\n========================")
    print("DIAGNOSTICS SUMMARY")
    print("========================")
    print("Stocks Scanned :", total_stocks)
    print("RSI Passed     :", rsi_pass)
    print("VWAP Passed    :", vwap_pass)
    print("EMA5 Passed    :", ema5_pass)
    print("EMA15 Passed   :", ema15_pass)
    print("Volume Passed  :", volume_pass)
    print("Market Passed  :", market_pass)
    print("========================\n")

    return results