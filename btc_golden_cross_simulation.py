import numpy as np
import pandas as pd

def generate_btc_prices(days=60, initial_price=60000.0, annual_drift=0.15, annual_volatility=0.70, seed=42):
    """
    Simulates daily Bitcoin prices using Geometric Brownian Motion (GBM).
    """
    if seed is not None:
        np.random.seed(seed)

    dt = 1 / 365.0  # Daily time step
    daily_drift = (annual_drift - 0.5 * annual_volatility**2) * dt
    daily_vol = annual_volatility * np.sqrt(dt)

    random_shocks = np.random.normal(0, 1, days)
    daily_returns = np.exp(daily_drift + daily_vol * random_shocks)

    prices = [initial_price]
    for r in daily_returns[:-1]:
        prices.append(prices[-1] * r)

    dates = pd.date_range(start=pd.Timestamp.now().floor('D') - pd.Timedelta(days=days-1), periods=days, freq='D')

    df = pd.DataFrame({
        'Day': range(1, days + 1),
        'Date': dates.strftime('%Y-%m-%d'),
        'Price': np.round(prices, 2)
    })

    # Calculate 7-day and 30-day Moving Averages
    df['MA7'] = df['Price'].rolling(window=7, min_periods=1).mean().round(2)
    df['MA30'] = df['Price'].rolling(window=30, min_periods=1).mean().round(2)

    return df

def simulate_golden_cross_strategy(df, initial_cash=10000.0):
    """
    Simulates a Golden Cross trading strategy on simulated BTC price data.
    """
    cash = float(initial_cash)
    btc_held = 0.0
    position = "CASH"  # "CASH" or "BTC"

    history = []

    for i in range(len(df)):
        row = df.iloc[i]
        day = row['Day']
        date = row['Date']
        price = row['Price']
        ma7 = row['MA7']
        ma30 = row['MA30']

        signal = "HOLD"
        action = "HOLD"

        if i > 0:
            prev_ma7 = df.iloc[i-1]['MA7']
            prev_ma30 = df.iloc[i-1]['MA30']

            # Golden Cross: MA7 was <= MA30 and is now > MA30
            if prev_ma7 <= prev_ma30 and ma7 > ma30:
                signal = "GOLDEN CROSS"
                if position == "CASH" and cash > 0:
                    btc_held = cash / price
                    cash = 0.0
                    position = "BTC"
                    action = "BUY"
                else:
                    action = "HOLD BTC"

            # Death Cross: MA7 was >= MA30 and is now < MA30
            elif prev_ma7 >= prev_ma30 and ma7 < ma30:
                signal = "DEATH CROSS"
                if position == "BTC" and btc_held > 0:
                    cash = btc_held * price
                    btc_held = 0.0
                    position = "CASH"
                    action = "SELL"
                else:
                    action = "HOLD CASH"

        total_value = cash + (btc_held * price)

        history.append({
            'Day': day,
            'Date': date,
            'Price': price,
            'MA7': ma7,
            'MA30': ma30,
            'Signal': signal,
            'Action': action,
            'Cash': round(cash, 2),
            'BTC': round(btc_held, 6),
            'TotalValue': round(total_value, 2)
        })

    return pd.DataFrame(history)

def print_simulation_report(ledger_df, initial_cash=10000.0):
    """
    Prints a formatted daily trading ledger and final performance summary.
    """
    print("=" * 105)
    print(" " * 32 + "60-DAY BITCOIN GOLDEN CROSS TRADING LEDGER")
    print("=" * 105)
    header = f"{'Day':<5} | {'Date':<10} | {'BTC Price ($)':<13} | {'MA7 ($)':<10} | {'MA30 ($)':<10} | {'Signal/Action':<15} | {'Cash ($)':<10} | {'BTC Held':<10} | {'Total Portfolio ($)':<18}"
    print(header)
    print("-" * 105)

    for _, row in ledger_df.iterrows():
        action_str = f"{row['Signal']} -> {row['Action']}" if row['Signal'] != "HOLD" else "HOLD"
        print(f"{row['Day']:<5} | {row['Date']:<10} | ${row['Price']:<12,.2f} | ${row['MA7']:<9,.2f} | ${row['MA30']:<9,.2f} | {action_str:<15} | ${row['Cash']:<9,.2f} | {row['BTC']:<10.6f} | ${row['TotalValue']:<17,.2f}")

    print("=" * 105)

    # Calculate performance metrics
    start_price = ledger_df.iloc[0]['Price']
    end_price = ledger_df.iloc[-1]['Price']
    final_strategy_value = ledger_df.iloc[-1]['TotalValue']

    strategy_return = ((final_strategy_value - initial_cash) / initial_cash) * 100.0

    buy_and_hold_btc = initial_cash / start_price
    buy_and_hold_final_value = buy_and_hold_btc * end_price
    buy_and_hold_return = ((buy_and_hold_final_value - initial_cash) / initial_cash) * 100.0

    trades = ledger_df[ledger_df['Action'].isin(['BUY', 'SELL'])]
    num_trades = len(trades)

    print("\n" + "=" * 50)
    print(" " * 12 + "FINAL PORTFOLIO PERFORMANCE SUMMARY")
    print("=" * 50)
    print(f" Initial Portfolio Cash     : ${initial_cash:,.2f}")
    print(f" Starting BTC Price (Day 1) : ${start_price:,.2f}")
    print(f" Ending BTC Price (Day 60)   : ${end_price:,.2f}")
    print(f" Total Trades Executed       : {num_trades}")
    print("-" * 50)
    print(f" Final Golden Cross Value   : ${final_strategy_value:,.2f} ({strategy_return:+.2f}%)")
    print(f" Final Buy & Hold Value     : ${buy_and_hold_final_value:,.2f} ({buy_and_hold_return:+.2f}%)")

    outperformance = strategy_return - buy_and_hold_return
    print(f" Strategy Outperformance     : {outperformance:+.2f}%")
    print("=" * 50 + "\n")

def main():
    initial_cash = 10000.0
    df = generate_btc_prices(days=60, initial_price=60000.0, seed=42)
    ledger_df = simulate_golden_cross_strategy(df, initial_cash=initial_cash)
    print_simulation_report(ledger_df, initial_cash=initial_cash)

if __name__ == '__main__':
    main()
