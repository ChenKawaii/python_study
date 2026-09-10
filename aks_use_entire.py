import akshare as ak
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# AI根据aks_use.py生成

# ============================================================
# 1. 数据获取
# ============================================================
def get_stock_data(stock_symbol, start_date, end_date) -> pd.DataFrame:
    """获取A股历史日线数据"""

    stock_symbol = stock_symbol.lower()
    stock_data = ak.stock_zh_a_daily(symbol=stock_symbol, start_date=start_date, end_date=end_date)
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    stock_data = stock_data.set_index('date').sort_index()
    return stock_data


# ============================================================
# 2. 信号生成（支持任意均线窗口）
# ============================================================
def gen_trade_signal(df, short_window=5, long_window=20) -> pd.DataFrame:
    """
    生成双均线交易信号。

    Parameters:
    df (pd.DataFrame): 含 'close' 列的行情数据
    short_window (int): 短期均线窗口，如 5
    long_window (int): 长期均线窗口，如 20

    Returns:
    pd.DataFrame: 新增 MA_short / MA_long / Signal / Position 列
    """
    df = df.copy()  # 避免修改原始数据

    df[f'MA{short_window}'] = df['close'].rolling(window=short_window).mean()
    df[f'MA{long_window}'] = df['close'].rolling(window=long_window).mean()

    # 金叉买入(1)，死叉空仓(0)
    df['Signal'] = np.where(
        df[f'MA{short_window}'] > df[f'MA{long_window}'], 1, 0
    )
    df['Position'] = df['Signal'].diff()  # +1 买入，-1 卖出

    return df


# ============================================================
# 3. 回测引擎（封装交易逻辑）
# ============================================================
def run_backtest(df, short_window=5, long_window=20,
                 initial_cash=5_000_000,
                 commission_rate=0.0003,
                 stamp_duty_rate=0.001) -> dict:
    """
    执行回测，返回绩效指标和交易记录。

    Returns:
    dict: 含 total_assets, cumulative_return, sharpe_ratio,
          max_drawdown, win_rate, profit_factor, trades 等
    """
    df = gen_trade_signal(df, short_window, long_window)

    hold = 0
    cash = initial_cash
    total_assets = []
    buy_trades, sell_trades = [], []

    for i in range(len(df)):
        price = df['close'].iloc[i]

        if i == 0:
            total_assets.append(initial_cash)
            continue

        # 买入信号
        if df['Position'].iloc[i] == 1 and cash > 100 * price:
            hands = int(cash // (price * 100))
            if hands > 0:
                hold += hands * 100
                cash -= hands * price * 100 * (1 + commission_rate)
                buy_trades.append({
                    'date': df.index[i], 'price': price,
                    'shares': hands * 100
                })

        # 卖出信号
        elif df['Position'].iloc[i] == -1 and hold > 0:
            cash += hold * price * (1 - commission_rate - stamp_duty_rate)
            sell_trades.append({
                'date': df.index[i], 'price': price, 'shares': hold
            })
            hold = 0

        total_assets.append(cash + hold * price)

    df['Total Assets'] = total_assets
    df['Cumulative Return'] = df['Total Assets'] / initial_cash - 1

    # ---- 绩效指标 ----
    perf = calc_performance(df, buy_trades, sell_trades, initial_cash)
    perf['trades'] = {'buy': buy_trades, 'sell': sell_trades}
    perf['df'] = df
    return perf


# ============================================================
# 4. 绩效计算（独立函数，便于复用）
# ============================================================
def calc_performance(df, buy_trades, sell_trades, initial_cash) -> dict:
    """计算夏普比率、最大回撤、胜率、盈亏比"""
    # 夏普比率
    daily_ret = df['Total Assets'].pct_change()
    annual_ret = daily_ret.mean() * 252
    annual_vol = daily_ret.std() * np.sqrt(252)
    sharpe = (annual_ret - 0.03) / annual_vol if annual_vol != 0 else np.nan

    # 最大回撤（保留负号）
    running_max = df['Total Assets'].cummax()
    drawdown_pct = (df['Total Assets'] - running_max) / running_max
    max_dd = drawdown_pct.min()

    # 胜率 & 盈亏比（只统计配对完成的交易）
    win_count, loss_count = 0, 0
    total_win, total_loss = 0, 0
    pair_count = min(len(buy_trades), len(sell_trades))
    for i in range(pair_count):
        buy_p = buy_trades[i]['price']
        sell_p = sell_trades[i]['price']
        shares = buy_trades[i]['shares']
        if sell_p > buy_p:
            win_count += 1
            total_win += (sell_p - buy_p) * shares
        else:
            loss_count += 1
            total_loss += (buy_p - sell_p) * shares

    win_rate = win_count / pair_count if pair_count > 0 else np.nan
    profit_factor = total_win / total_loss if total_loss != 0 else np.nan

    return {
        'cumulative_return': df['Cumulative Return'].iloc[-1],
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'total_trades': pair_count,
        'final_assets': df['Total Assets'].iloc[-1],
    }


# ============================================================
# 5. 参数对比（核心新增功能）
# ============================================================
def compare_params(df, param_pairs) -> pd.DataFrame:
    """
    对多组均线参数跑回测，返回对比表。

    Parameters:
    df (pd.DataFrame): 原始行情数据
    param_pairs (list): [(short, long), ...] 如 [(5,20), (10,30), (5,60)]

    Returns:
    pd.DataFrame: 每组参数的绩效指标对比
    """
    results = []
    for short, long in param_pairs:
        perf = run_backtest(df, short, long)
        results.append({
            '参数组合': f'MA{short}/MA{long}',
            '累计收益率': f"{perf['cumulative_return'] * 100:.2f}%",
            '夏普比率': f"{perf['sharpe_ratio']:.2f}",
            '最大回撤': f"{perf['max_drawdown'] * 100:.2f}%",
            '胜率': f"{perf['win_rate'] * 100:.2f}%",
            '盈亏比': f"{perf['profit_factor']:.2f}",
            '交易次数': perf['total_trades'],
        })
    return pd.DataFrame(results)


# ============================================================
# 6. 主程序
# ============================================================
def main():
    stock_symbol = 'sh600519'
    start_date = '2023-01-01'
    end_date = '2024-01-01'

    stock_data = get_stock_data(stock_symbol, start_date, end_date)

    # ---- 单次回测（保留原有功能）----
    perf = run_backtest(stock_data, short_window=5, long_window=20)
    print(f"\n{'='*60}")
    print(f"单次回测：MA5/MA20")
    print(f"累计收益率: {perf['cumulative_return']*100:.2f}%")
    print(f"夏普比率: {perf['sharpe_ratio']:.2f}")
    print(f"最大回撤: {perf['max_drawdown']*100:.2f}%")
    print(f"胜率: {perf['win_rate']*100:.2f}%")
    print(f"盈亏比: {perf['profit_factor']:.2f}")

    # ---- 参数对比 ----
    param_pairs = [(5, 20), (10, 30), (5, 60), (10, 60), (20, 60)]
    comparison = compare_params(stock_data, param_pairs)

    print(f"\n{'='*60}")
    print("参数对比结果：")
    print(comparison.to_string(index=False))

    # 保存对比表到 CSV（方便贴到 README）
    comparison.to_csv('param_comparison.csv', index=False, encoding='utf-8-sig')
    print("\n对比表已保存至 param_comparison.csv")


if __name__ == "__main__":
    main()