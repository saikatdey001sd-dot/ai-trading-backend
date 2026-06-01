import yfinance as yf
from ta.momentum import RSIIndicator

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

print("\n========== BACKTEST V2 RESULTS ==========\n")

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

        close = data["Close"].squeeze()
        volume = data["Volume"].squeeze()

        data["RSI"] = RSIIndicator(
            close=close,
            window=14
        ).rsi()

        data["EMA9"] = close.ewm(
            span=9,
            adjust=False
        ).mean()

        data["EMA20"] = close.ewm(
            span=20,
            adjust=False
        ).mean()

        # VWAP
        vwap = (
            (close * volume).cumsum()
            / volume.cumsum()
        )

        # Average Volume
        avg_volume = volume.rolling(20).mean()

        wins = 0
        losses = 0

        for i in range(20, len(data) - 5):

            price = float(close.iloc[i])

            rsi = float(data["RSI"].iloc[i])

            ema9 = float(data["EMA9"].iloc[i])

            ema20 = float(data["EMA20"].iloc[i])

            current_vwap = float(vwap.iloc[i])

            current_volume = float(volume.iloc[i])

            current_avg_volume = float(
                avg_volume.iloc[i]
            )

            score = 0

            # RSI
            if rsi > 50:
                score += 1

            # VWAP
            if price > current_vwap:
                score += 2

            # EMA Trend
            if ema9 > ema20:
                score += 3

            # Volume
            if (
                current_avg_volume > 0
                and current_volume >
                current_avg_volume
            ):
                score += 1

            # BUY SIGNAL
            if score >= 6:

                entry = price

                target = entry * 1.01

                stoploss = entry * 0.99

                future_prices = close.iloc[
                    i:i+5
                ]

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
    f"Win Rate   : "
    f"{overall_win_rate:.2f}%"
)

print("=============================")