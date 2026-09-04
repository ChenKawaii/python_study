import akshare as ak
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def get_stock_data(stock_symbol, start_date, end_date) -> pd.DataFrame:
    """
    Fetch historical stock data for a given stock symbol between specified dates.

    Parameters:
    stock_symbol (str): The stock symbol to fetch data for.
    start_date (str): The start date in 'YYYY-MM-DD' format.
    end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
    pd.DataFrame: A DataFrame containing the historical stock data.
    """
    # Fetch historical stock data using akshare
    stock_data = ak.stock_zh_a_daily(symbol=stock_symbol, start_date=start_date, end_date=end_date)
    
    # Convert the index to datetime
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    stock_data = stock_data.set_index('date')
    stock_data = stock_data.sort_index()  # Ensure the data is sorted by date

    return stock_data

def show_MA(stock_data, window=20) -> pd.Series:
    """
    Calculate and display the moving average(MA) of the stock data.

    Parameters:
    stock_data (pd.DataFrame): The DataFrame containing historical stock data.
    window (int): The window size for calculating the moving average.

    Day Price
    1   10
    2   11
    3   9
    4   10
    5   12  (MA = (10+11+9+10+12)/5 = 10.4)
    6   13  (MA = (11+9+10+12+13)/5 = 11.0) different from MA day 5,so it's changable
    By the way, the window size can be adjusted to calculate the moving average over different periods.

    Returns:
    pd.Series: A Series containing the moving average values.
    """
    # Calculate the moving average
    ma = stock_data['close'].rolling(window=window).mean()
    
    return ma # df Series

def genTradeSignal(df) -> pd.DataFrame:
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA5'] = df['close'].rolling(window=5).mean()

    df['Signal'] = np.where(df['MA5'] > df['MA20'], 1, 0)  # Buy signal when MA5 crosses above MA20
    df['Position'] = df['Signal'].diff()  # Calculate the difference to identify changes in position
    """
    Position means the change in trading position (buy/sell) based on the trade signals.
    1 buy -1 sell 0 hold
    """
    return df

def plot_trade_signals(df, stock_symbol):
    """
    Plot the stock price along with moving averages and trade signals.

    Parameters:
    df (pd.DataFrame): The DataFrame containing historical stock data and trade signals.
    stock_symbol (str): The stock symbol for labeling the plot.
    """
    try:
        plt.figure(figsize=(14, 7))
        plt.plot(df.index, df['close'], label='Close Price', color='blue')
        plt.plot(df.index, df['MA20'], label='20-Day MA', color='orange')
        plt.plot(df.index, df['MA5'], label='5-Day MA', color='green')

        buy_signals = df[df['Position'] == 1]
        plt.scatter(buy_signals.index, buy_signals['close'], label='Buy Signal', marker='^', color='g', s=100)

        sell_signals = df[df['Position'] == -1]
        plt.scatter(sell_signals.index, sell_signals['close'], label='Sell Signal', marker='v', color='r', s=100)

        plt.title(f'{stock_symbol} Price and Trade Signals')
        plt.xlabel('Date')
        plt.ylabel('Price(CNY)')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.savefig(f'{stock_symbol}_trading_signals.png')  
        print(f"Plot saved as {stock_symbol}_trading_signals.png")
        plt.close()  
    except Exception as e:
        print(f"Plotting error: {e}")

def main():
    stock_symbol = 'sh600519'  # Example stock symbol (Kweichow Moutai)
    period = 'daily'
    start_date = '2025-01-01'
    end_date = '2026-01-01'

    initial_cash = 5000000  # Total assets in CNY
    hold = 0  # Initial holding quantity
    cash = initial_cash  # Initial cash available
    total_assets = []  # List to track total assets over time
    trade_records = []  # List to record trade transactions

    # Fetch historical stock data
    stock_data = get_stock_data(stock_symbol, start_date, end_date)

    # Generate trade signals based on moving averages
    stock_data = genTradeSignal(stock_data)

    # Plot the stock price along with moving averages and trade signals
    plot_trade_signals(stock_data, stock_symbol)

    #
    for i in range(len(stock_data)):
        price = stock_data['close'].iloc[i]

        # the first day, we don't have any trade signals yet, so we just record the initial cash
        if i == 0:
            total_assets.append(initial_cash)
            continue

        # trade logic based on the generated trade signals
        # 1. Buy signal: If the position is 1 (buy) and we have enough cash, we buy as much as possible
        # 2. Sell signal: If the position is -1 (sell) and we have holdings, we sell all holdings
        if stock_data['Position'].iloc[i] == 1 and cash > 100 * price:  # Buy signal and enough cash to buy at least 100 shares
            # hold = cash // (price * 100)  # Calculate how many shares we can buy
            # cash -= hold * (price * 100)  # Deduct the cost from cash
            # print(f"Buy {hold} shares at {price} CNY on {stock_data.index[i].date()}")
            hands_to_buy = int(cash // (price * 100))
            if hands_to_buy > 0:
                hold += hands_to_buy * 100  # Update holdings
                cash -= hands_to_buy * price * 100  # Deduct the cost from cash
                trade_records.append({
                    'date': stock_data.index[i],
                    'type': 'BUY',
                    'price': price,
                    'shares': hands_to_buy * 100,
                    'amount': hands_to_buy * price * 100
                })
                print(f"Buy {hands_to_buy * 100} shares at {price} CNY on {stock_data.index[i].date()}")
        elif stock_data['Position'].iloc[i] == -1 and hold > 0:  # Sell signal and holdings
            cash += hold * price   # Add the proceeds to cash
            trade_records.append({
                'date': stock_data.index[i],
                'type': 'SELL',
                'price': price,
                'shares': hold,
                'amount': hold * price
            })
            print(f"Sell {hold} shares at {price} CNY on {stock_data.index[i].date()}")
            hold = 0  # Reset holdings

        # Calculate the daily total assets (cash + value of holdings)
        total_assets.append(cash + hold * price)

    stock_data['Total Assets'] = total_assets
    stock_data['Cumulative Return'] = stock_data['Total Assets'] / initial_cash - 1

    total_signals = len(stock_data[stock_data['Position'] != 0])
    total_executed = len(trade_records)

    # ================================================================================================
    # Calculate the sharpe ratio
    # daily_return means the percentage change in total assets from one day to the next
    # pct_change() calculates the percentage change between the current and prior element,like today's total assets vs yesterday's total assets
    stock_data['daily_return'] = stock_data['Total Assets'].pct_change()
    avg_daily_return = stock_data['daily_return'].mean()
    std_daily_return = stock_data['daily_return'].std()

    # annual_return is the average daily return multiplied by the number of trading days in a year (252), 
    # and annual_volatility is the standard deviation of daily returns multiplied by the square root of 252. 
    annual_return = avg_daily_return * 252  # Assuming 252 trading days in a year

    # annual_volatility is the standard deviation of daily returns multiplied by the square root of 252, 
    # which gives an estimate of the annualized volatility of the returns.
    annual_volatility = std_daily_return * np.sqrt(252)

    # risk_free_rate is the return of an investment with almost zero risk, often represented by government bonds.
    # In this case, we assume a risk-free rate of 3% (0.03).
    risk_free_rate = 0.03  # Assuming a risk-free rate of 3%

    # Calculate the Sharpe ratio, which means how much can you earn for every risk you take
    # It is calculated as the difference between the annual return and the risk-free rate, divided by the annual volatility.
    # If the annual volatility is zero (which would indicate no variability in returns), we set the Sharpe ratio to NaN to avoid division by zero.
    # Sharpe ratio    then
    # <0              Why not deposit in a bank
    # 0~1             Not bad, but not good enough
    # 1~2             Good, you can consider investing more
    # >2              Excellent, you can consider investing more and more
    
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility != 0 else np.nan


    # Output the DataFrame with trade signals to a CSV file
    print(f"\n{'='*50}")
    print(f"Total signals generated: {total_signals} times")
    print(f"Total trades executed: {total_executed} times")
    print(f"Final price: {stock_data['close'].iloc[-1]:.2f} CNY")
    print(f"Final total assets: {stock_data['Total Assets'].iloc[-1]:.2f} CNY")
    print(f'Final cumulative return: {stock_data["Cumulative Return"].iloc[-1] * 100:.2f}%')
    print(f'Final Sharpe Ratio: {sharpe_ratio:.2f}')
    if trade_records:
        print(f"\nExecuted Trades:")
        for trade in trade_records:
            print(f"  {trade['date'].date()}: {trade['type']} {trade['shares']} shares at {trade['price']:.2f} CNY (Total: {trade['amount']:.2f} CNY)")

if __name__ == "__main__":
    main()