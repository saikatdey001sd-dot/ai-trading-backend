import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

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

overall_wins = 0
overall_losses = 0

print("\n========== BACKTEST V3 RESULTS ==========\n")

for symbol in stocks:

    try:

        data = yf.download(
            symbol,
            period="1mo",
            interval="15m",
            auto_adjust=True,
            progress=False
        )

        if data.empty:
            continue

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        close = data["Close"]

        # RSI
        data["RSI"] = RSIIndicator(
            close=close,
            window=14
        ).rsi()

        # VWAP
        data["VWAP"] = (
            (data["Close"] * data["Volume"]).cumsum()
            / data["Volume"].cumsum()
        )

        # EMA
        data["EMA9"] = close.ewm(
            span=9,
            adjust=False
        ).mean()

        data["EMA20"] = close.ewm(
            span=20,
            adjust=False
        ).mean()

        # ATR
        atr = AverageTrueRange(
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            window=14
        )

        data["ATR"] = atr.average_true_range()

        # Volume
        data["AvgVolume"] = (
            data["Volume"]
            .rolling(20)
            .mean()
        )

        wins = 0
        losses = 0

        for i in range(30, len(data) - 10):

            score = 0

            price = data["Close"].iloc[i]

            rsi = data["RSI"].iloc[i]

            vwap = data["VWAP"].iloc[i]

            ema9 = data["EMA9"].iloc[i]

            ema20 = data["EMA20"].iloc[i]

            volume = data["Volume"].iloc[i]

            avg_volume = data["AvgVolume"].iloc[i]

            atr_value = data["ATR"].iloc[i]

            # RSI
            if rsi > 50:
                score += 1

            # VWAP
            if price > vwap:
                score += 2

            # EMA
            if ema9 > ema20:
                score += 3

            # Volume
            if volume > avg_volume:
                score += 1

            # Simulated Market Trend
            if ema20 > data["EMA20"].iloc[i - 5]:
                score += 2

            # BUY CONDITION
            if score >= 7:

                entry = price

                target = (
                    entry
                    + (2 * atr_value)
                )

                stoploss = (
                    entry
                    - atr_value
                )

                future_prices = (
                    data["Close"]
                    .iloc[i:i+10]
                )

                if future_prices.max() >= target:
                    wins += 1

                elif future_prices.min() <= stoploss:
                    losses += 1

        total = wins + losses

        if total > 0:
            win_rate = (
                wins / total
            ) * 100
        else:
            win_rate = 0

        overall_wins += wins
        overall_losses += losses

        print(
            f"{symbol:15} "
            f"Wins={wins:<3} "
            f"Losses={losses:<3} "
            f"Win Rate={win_rate:.2f}%"
        )

    except Exception as e:

        print(
            f"{symbol} Error: {e}"
        )

overall_total = (
    overall_wins
    + overall_losses
)

if overall_total > 0:

    overall_win_rate = (
        overall_wins
        / overall_total
    ) * 100

else:

    overall_win_rate = 0

print("\n========== OVERALL ==========")

print(
    f"Wins       : {overall_wins}"
)

print(
    f"Losses     : {overall_losses}"
)

print(
    f"Total      : {overall_total}"
)

print(
    f"Win Rate   : {overall_win_rate:.2f}%"
)

print("=============================")