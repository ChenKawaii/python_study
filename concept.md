# 量化策略项目金融概念解析



>
>本文档整理 aks_use_entire.py 项目中涉及的核心金融概念，包括概念定义、常态计算方法，以及如何用 Python 实现。适合作为项目配套学习资料，也方便面试前快速复习。



**📑 目录**

1. 双均线策略（Dual Moving Average）
2. 金叉与死叉（Golden Cross / Death Cross）
3. 移动平均线（MA）
4. ADX 趋势强度指标
5. +DI / -DI 方向指标
6. RSI 相对强弱指标
7. 成交量过滤（Volume Filter）
8. 累计收益率（Cumulative Return）
9. 夏普比率（Sharpe Ratio）
10. 最大回撤（Maximum Drawdown）
11. 胜率（Win Rate）
12. 盈亏比（Profit Factor）
13. 交易成本（佣金 + 印花税）
14. 前视偏差（Look-ahead Bias）
15. 过拟合（Overfitting）

---



## 1. 双均线策略（Dual Moving Average）

### 📖 概念

双均线策略是最经典的趋势跟踪策略之一。它使用两条不同周期的移动平均线：

- **短期均线（如 MA5）**：反映近期价格动能
- **长期均线（如 MA20）**：反映中期趋势方向

**核心逻辑**：当短期均线向上穿越长期均线时，说明近期动能转强，视为买入信号；当短期均线向下穿越长期均线时，说明动能转弱，视为卖出信号。

### 🧮 常态计算方法

1. 计算短期均线：`MA_short = close.rolling(short_window).mean()`
2. 计算长期均线：`MA_long = close.rolling(long_window).mean()`
3. 生成信号：`Signal = 1 if MA_short > MA_long else 0`
4. 标记买卖点：`Position = Signal.diff()`

### 🐍 Python 实现

```python
import pandas as pd
import numpy as np

def dual_ma_signal(df, short_window=5, long_window=20):
    df = df.copy()
    df[f'MA{short_window}'] = df['close'].rolling(window=short_window).mean()
    df[f'MA{long_window}'] = df['close'].rolling(window=long_window).mean()
    
    # 金叉=1，死叉=0
    df['Signal'] = np.where(df[f'MA{short_window}'] > df[f'MA{long_window}'], 1, 0)
    # +1 买入，-1 卖出，0 持有
    df['Position'] = df['Signal'].diff()
    
    return df
```



### ⚠️ 注意事项

- 双均线是**趋势跟踪**策略，在单边行情中表现好，在震荡市中会频繁产生假信号
- 参数选择（5/20、10/30、20/60）对结果影响很大
- 短期均线与长期均线的**周期差不宜过大**，否则长期均线滞后性会导致信号严重滞后

---------

## 2. 金叉与死叉（Golden Cross / Death Cross）

### 📖 概念

- **金叉（Golden Cross）**：短期均线上穿长期均线，视为买入信号
- **死叉（Death Cross）**：短期均线下穿长期均线，视为卖出信号

这两个术语源于均线交叉在图表上形成的"X"形，是技术分析中最广为人知的信号之一。

### 🧮 常态计算方法

通过比较相邻两天的 `MA_short - MA_long` 差值符号变化来判断：

- 昨天 `MA_short < MA_long`，今天 `MA_short > MA_long` → 金叉
- 昨天 `MA_short > MA_long`，今天 `MA_short < MA_long` → 死叉

### 🐍 Python 实现

python

```
# 方法1：用 Signal.diff() 自动捕捉交叉点
df['Signal'] = np.where(df['MA5'] > df['MA20'], 1, 0)
df['Position'] = df['Signal'].diff()
# Position == 1  → 金叉（买入）
# Position == -1 → 死叉（卖出）

# 方法2：显式判断交叉
df['Cross'] = np.sign(df['MA5'] - df['MA20']).diff()
# Cross == 2  → 金叉
# Cross == -2 → 死叉
```



### ⚠️ 注意事项

- 金叉/死叉是**滞后信号**，均线本身是历史价格的平均，交叉发生时趋势往往已经走了一段
- 在震荡市中，金叉/死叉会频繁交替出现，产生大量假信号
- 这正是项目中引入 ADX、RSI、成交量过滤的原因

------

## 3. 移动平均线（MA）

### 📖 概念

移动平均线（Moving Average）是过去 N 天收盘价的算术平均值。它平滑了价格波动，帮助识别趋势方向。

**常见类型**：

| 类型                    | 计算方式                     | 特点                 |
| :---------------------- | :--------------------------- | :------------------- |
| **SMA（简单移动平均）** | 过去 N 天收盘价之和 / N      | 最常用，各天权重相同 |
| **EMA（指数移动平均）** | 加权平均，近期权重更大       | 反应更快，但波动更大 |
| **WMA（加权移动平均）** | 按时间加权，近期权重线性递增 | 介于 SMA 和 EMA 之间 |

### 🧮 常态计算方法

**SMA**：`MA_t = (P_t + P_{t-1} + ... + P_{t-N+1}) / N`

**EMA**：`EMA_t = α × P_t + (1 - α) × EMA_{t-1}`，其中 `α = 2 / (N + 1)`

### 🐍 Python 实现

python

```
# SMA
df['MA20'] = df['close'].rolling(window=20).mean()

# EMA
df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()

# Wilder's 平滑（用于 ADX/RSI，等价于 alpha=1/N 的 EMA）
df['Wilder20'] = df['close'].ewm(alpha=1/20, adjust=False).mean()
```



### ⚠️ 注意事项

- `rolling(window=N).mean()` 的前 N-1 天是 `NaN`，因为数据不足
- `ewm(adjust=False)` 是 Wilder's 平滑的标准写法，`adjust=True` 会得到不同结果
- MA 是**滞后指标**，周期越长滞后越严重

------

## 4. ADX 趋势强度指标

### 📖 概念

ADX（Average Directional Index，平均趋向指数）由 Welles Wilder 提出，用于衡量**趋势的强度**，不判断方向。

| ADX 数值 | 含义                     |
| :------- | :----------------------- |
| < 20     | 趋势弱，震荡行情         |
| 20 ~ 25  | 趋势模糊，观望           |
| 25 ~ 40  | 趋势明确，顺势交易胜率高 |
| 40 ~ 60  | 趋势强，单边行情         |
| > 60     | 趋势火热，存在反转风险   |

### 🧮 常态计算方法

ADX 的计算分为五步：

**第1步：计算 +DM 和 -DM**

- `+DM = high_t - high_{t-1}`，若为正且大于 `low_{t-1} - low_t`
- `-DM = low_{t-1} - low_t`，若为正且大于 `high_t - high_{t-1}`

**第2步：计算 TR（真实波幅）**

- `TR = max(high - low, |high - close_{t-1}|, |close_{t-1} - low|)`

**第3步：平滑 +DM、-DM、TR**

- 使用 Wilder's 平滑：`smoothed = ewm(alpha=1/period, adjust=False).mean()`

**第4步：计算 +DI 和 -DI**

- `+DI = 100 × +DM_smooth / TR_smooth`
- `-DI = 100 × -DM_smooth / TR_smooth`

**第5步：计算 DX 和 ADX**

- `DX = 100 × |+DI - -DI| / (+DI + -DI)`
- `ADX = DX.ewm(alpha=1/period, adjust=False).mean()`

### 🐍 Python 实现

python

```
def calc_adx(df, period=14):
    df = df.copy()
    
    # 1. 计算 +DM / -DM
    df['high_diff'] = df['high'].diff()
    df['low_diff'] = -df['low'].diff()
    df['+DM'] = np.where((df['high_diff'] > df['low_diff']) & (df['high_diff'] > 0), 
                          df['high_diff'], 0)
    df['-DM'] = np.where((df['low_diff'] > df['high_diff']) & (df['low_diff'] > 0), 
                          df['low_diff'], 0)
    
    # 2. 计算 TR
    df['HL'] = df['high'] - df['low']
    df['HC'] = abs(df['high'] - df['close'].shift(1))
    df['LC'] = abs(df['close'].shift(1) - df['low'])
    df['TR'] = df[['HL', 'HC', 'LC']].max(axis=1)
    
    # 3. Wilder's 平滑
    df['+DM_smooth'] = df['+DM'].ewm(alpha=1/period, adjust=False).mean()
    df['-DM_smooth'] = df['-DM'].ewm(alpha=1/period, adjust=False).mean()
    df['TR_smooth'] = df['TR'].ewm(alpha=1/period, adjust=False).mean()
    
    # 4. 计算 +DI / -DI
    df['+DI'] = 100 * (df['+DM_smooth'] / df['TR_smooth'])
    df['-DI'] = 100 * (df['-DM_smooth'] / df['TR_smooth'])
    
    # 5. 计算 DX 和 ADX
    df['DX'] = 100 * (abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI']))
    df['ADX'] = df['DX'].ewm(alpha=1/period, adjust=False).mean()
    
    return df
```



### ⚠️ 注意事项

- ADX 经过**两次平滑**（DX 平滑 + ADX 平滑），反应非常慢
- 当 ADX 确认趋势时，行情可能已经走完大半，容易买在高点
- 项目中 ADX 过滤在 10 只股票上全部恶化，正是这个滞后性导致的

------

## 5. +DI / -DI 方向指标

### 📖 概念

+DI（正向方向指标）和 -DI（负向方向指标）是 ADX 的组成部分，用于判断**趋势的方向**：

- `+DI > -DI`：多头占优，趋势向上
- `+DI < -DI`：空头占优，趋势向下
- `+DI ≈ -DI`：多空均衡，趋势不明

### 🧮 常态计算方法

见 ADX 计算第 4 步：`+DI = 100 × +DM_smooth / TR_smooth`

### 🐍 Python 实现

python

```
df['+DI'] = 100 * (df['+DM_smooth'] / df['TR_smooth'])
df['-DI'] = 100 * (df['-DM_smooth'] / df['TR_smooth'])

# 买入条件：+DI > -DI（趋势向上）
buy_condition = df['+DI'] > df['-DI']
```



### ⚠️ 注意事项

- +DI/-DI 反应比 ADX 快，但仍有滞后
- 单独使用 +DI/-DI 容易在震荡市中频繁反转
- 通常与 ADX 配合使用：ADX 判断趋势强度，+DI/-DI 判断方向

------

## 6. RSI 相对强弱指标

### 📖 概念

RSI（Relative Strength Index，相对强弱指标）由 Welles Wilder 提出，用于衡量价格的**超买或超卖状态**。

| RSI 数值 | 含义     | 市场状态           |
| :------- | :------- | :----------------- |
| > 70     | 超买     | 涨得太猛，可能回调 |
| 50 ~ 70  | 偏强     | 多头占优           |
| 50       | 多空均衡 | 中性               |
| 30 ~ 50  | 偏弱     | 空头占优           |
| < 30     | 超卖     | 跌得太狠，可能反弹 |

### 🧮 常态计算方法

**第1步：计算每日涨跌**

- `change = close_t - close_{t-1}`
- `gain = max(change, 0)`（上涨日）
- `loss = max(-change, 0)`（下跌日）

**第2步：计算平均涨跌幅**

- `avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()`
- `avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()`

**第3步：计算 RS 和 RSI**

- `RS = avg_gain / avg_loss`
- `RSI = 100 - 100 / (1 + RS)`

### 🐍 Python 实现

python

```
def calc_rsi(df, period=14):
    df = df.copy()
    df['change'] = df['close'].diff()
    df['gain'] = np.where(df['change'] > 0, df['change'], 0)
    df['loss'] = np.where(df['change'] < 0, -df['change'], 0)
    
    df['avg_gain'] = df['gain'].ewm(alpha=1/period, adjust=False).mean()
    df['avg_loss'] = df['loss'].ewm(alpha=1/period, adjust=False).mean()
    
    df['RS'] = df['avg_gain'] / df['avg_loss']
    df['RSI'] = 100 - (100 / (1 + df['RS']))
    
    return df
```



### ⚠️ 注意事项

- 当 `avg_loss = 0` 时，`RS = inf`，`RSI = 100`，需要特殊处理
- RSI 的常用周期是 14 天，短周期（如 6 天）更敏感，长周期（如 24 天）更平滑
- 项目中 RSI 过滤要求 `50 < RSI < 60`，既排除超买（> 60），又排除弱势中的金叉（< 50）

------

## 7. 成交量过滤（Volume Filter）

### 📖 概念

成交量过滤是技术分析中常用的信号确认方法。核心假设：**上涨需要成交量配合（放量上涨才可信），下跌不一定需要（缩量下跌也可能是正常调整）**。

因此，买入信号通常要求**成交量放大**，卖出信号不一定要求。

### 🧮 常态计算方法

1. 计算过去 N 日平均成交量：`Volume_MA = volume.rolling(N).mean()`
2. 判断是否放量：`Volume_Filter = volume > k × Volume_MA`（k 通常取 1.5 或 2）

### 🐍 Python 实现

python

```
df['Volume_MA20'] = df['volume'].rolling(window=20).mean()
df['Volume_Filter'] = df['volume'] > 1.5 * df['Volume_MA20']

# 买入条件叠加成交量过滤
buy_condition = base_condition and df['Volume_Filter']
```



### ⚠️ 注意事项

- 阈值 k 的选择对结果影响很大，1.5 倍较常用，但可能过严
- 成交量数据通常有**季节性**（如月末、季末放量），简单均值可能不够
- 项目中成交量过滤在 10 只股票上表现不稳定，交易次数普遍过少

------

## 8. 累计收益率（Cumulative Return）

### 📖 概念

累计收益率衡量策略从开始到结束的**总盈亏比例**。

```
累计收益率 = (最终总资产 / 初始资金) - 1
```

### 🧮 常态计算方法

1. 逐日计算总资产：`Total Assets = cash + hold × price`
2. 计算累计收益：`Cumulative Return = Total Assets / initial_cash - 1`

### 🐍 Python 实现

python

```
df['Total Assets'] = total_assets  # 逐日总资产列表
df['Cumulative Return'] = df['Total Assets'] / initial_cash - 1

# 最终累计收益率
final_return = df['Cumulative Return'].iloc[-1]
```



### ⚠️ 注意事项

- 累计收益率**不考虑时间**，同样 20% 收益，1 年 vs 5 年意义完全不同
- 必须结合**年化收益率**和**最大回撤**一起看
- 项目中紫金矿业基准 +166.78%，但最大回撤 -47.53%，风险极高

------

## 9. 夏普比率（Sharpe Ratio）

### 📖 概念

夏普比率衡量**每承担一单位风险获得的超额收益**，是风险调整后收益的核心指标。

```
夏普比率 = (年化收益 - 无风险利率) / 年化波动率
```

| 夏普比率 | 含义       |
| :------- | :--------- |
| < 0      | 不如存银行 |
| 0 ~ 1    | 一般       |
| 1 ~ 2    | 良好       |
| > 2      | 优秀       |

### 🧮 常态计算方法

1. 计算日收益率：`daily_ret = Total Assets.pct_change()`
2. 年化收益：`annual_ret = daily_ret.mean() × 252`
3. 年化波动率：`annual_vol = daily_ret.std() × √252`
4. 夏普比率：`(annual_ret - risk_free_rate) / annual_vol`

### 🐍 Python 实现

python

```
daily_ret = df['Total Assets'].pct_change()
annual_ret = daily_ret.mean() * 252
annual_vol = daily_ret.std() * np.sqrt(252)
risk_free_rate = 0.03

sharpe = (annual_ret - risk_free_rate) / annual_vol if annual_vol != 0 else np.nan
```



### ⚠️ 注意事项

- 无风险利率通常取**国债收益率**，项目中简化为 3%
- 年化交易日按 **252 天** 计算（A 股约 242 天，美股 252 天）
- 夏普比率对**极端值敏感**，少数几天的大涨大跌会显著影响结果
- 样本量太小时（如交易次数 < 10），夏普比率不稳定

------

## 10. 最大回撤（Maximum Drawdown）

### 📖 概念

最大回撤衡量策略从**历史最高点**到**最低点**的最大亏损幅度，反映最坏情况下的风险。

```
最大回撤 = min( (总资产 - 历史最高) / 历史最高 )
```

### 🧮 常态计算方法

1. 计算历史最高：`running_max = Total Assets.cummax()`
2. 计算回撤：`drawdown = (Total Assets - running_max) / running_max`
3. 取最小值：`max_dd = drawdown.min()`

### 🐍 Python 实现

python

```
running_max = df['Total Assets'].cummax()
drawdown_pct = (df['Total Assets'] - running_max) / running_max
max_dd = drawdown_pct.min()  # 返回负数，如 -0.1213

# 打印时保留负号（符合行业惯例）
print(f"最大回撤: {max_dd * 100:.2f}%")  # 输出 -12.13%
```



### ⚠️ 注意事项

- **必须保留负号**，行业惯例是 `-12.13%` 而非 `12.13%`
- 不要用 `abs().max()`，虽然数值等价，但会掩盖潜在 bug
- 最大回撤通常远大于最终收益，因为过程中可能大幅缩水后回升
- 项目中比亚迪基准最大回撤 -77.15%，这是极高的风险水平

------

## 11. 胜率（Win Rate）

### 📖 概念

胜率衡量**盈利交易占总交易的比例**。

```
胜率 = 盈利交易数 / 总交易数
```

### 🧮 常态计算方法

1. 配对买卖交易：第 i 次买入对应第 i 次卖出
2. 判断盈亏：`sell_price > buy_price` 为盈利
3. 统计胜率：`win_count / pair_count`

### 🐍 Python 实现

python

```
win_count, loss_count = 0, 0
pair_count = min(len(buy_trades), len(sell_trades))

for i in range(pair_count):
    buy_p = buy_trades[i]['price']
    sell_p = sell_trades[i]['price']
    if sell_p > buy_p:
        win_count += 1
    else:
        loss_count += 1

win_rate = win_count / pair_count if pair_count > 0 else np.nan
```



### ⚠️ 注意事项

- 只统计**配对完成**的交易，未平仓的买入不计入
- `pair_count = min(len(buy), len(sell))` 避免索引越界
- 胜率低不代表策略差：趋势跟踪策略通常胜率 30-40%，但盈亏比高
- 项目中基准胜率 32.61%，盈亏比 1.20，属于典型的趋势跟踪特征

------

## 12. 盈亏比（Profit Factor）

### 📖 概念

盈亏比衡量**总盈利与总亏损的比值**，反映盈利交易覆盖亏损交易的能力。

```
盈亏比 = 总盈利 / 总亏损
```

| 盈亏比 | 含义                     |
| :----- | :----------------------- |
| < 1    | 亏损大于盈利，策略不可行 |
| = 1    | 盈亏平衡                 |
| > 1    | 盈利大于亏损             |
| > 2    | 较好的策略               |

### 🧮 常态计算方法

1. 累加所有盈利交易的金额：`total_win`
2. 累加所有亏损交易的金额：`total_loss`
3. 计算比值：`total_win / total_loss`

### 🐍 Python 实现

python

```
total_win, total_loss = 0, 0

for i in range(pair_count):
    buy_p = buy_trades[i]['price']
    sell_p = sell_trades[i]['price']
    shares = buy_trades[i]['shares']
    
    if sell_p > buy_p:
        total_win += (sell_p - buy_p) * shares
    else:
        total_loss += (buy_p - sell_p) * shares

profit_factor = total_win / total_loss if total_loss != 0 else np.nan
```



### ⚠️ 注意事项

- 当 `total_loss = 0` 时，盈亏比为 `inf`，需要特殊处理
- 盈亏比与胜率需要**配合看**：
  - 高胜率 + 低盈亏比：频繁小赚，偶尔大亏
  - 低胜率 + 高盈亏比：频繁小亏，偶尔大赚（趋势跟踪）
- 项目中 RSI < 60 版本盈亏比 9.36，但只有 2 次交易，统计意义有限

------

## 13. 交易成本（佣金 + 印花税）

### 📖 概念

真实交易中，买卖股票需要支付以下成本：

| 成本类型   | 费率  | 收取方向 | 说明             |
| :--------- | :---- | :------- | :--------------- |
| **佣金**   | 0.03% | 买卖双向 | 券商收取，可协商 |
| **印花税** | 0.1%  | 仅卖出   | 国家收取，固定   |

### 🧮 常态计算方法

**买入时**：`cash -= shares × price × (1 + commission_rate)`

**卖出时**：`cash += shares × price × (1 - commission_rate - stamp_duty_rate)`

### 🐍 Python 实现

python

```
commission_rate = 0.0003   # 佣金 0.03%
stamp_duty_rate = 0.001    # 印花税 0.1%

# 买入
cash -= hands * price * 100 * (1 + commission_rate)

# 卖出
cash += hold * price * (1 - commission_rate - stamp_duty_rate)
```



### ⚠️ 注意事项

- 交易成本对**高频策略**影响巨大，频繁交易会显著侵蚀收益
- 项目中 MA5/MA20 交易 46 次，成本累积明显
- 实际还有**滑点**（买卖价差）、**冲击成本**（大额订单影响价格），回测中未建模

------

## 14. 前视偏差（Look-ahead Bias）

### 📖 概念

前视偏差指在回测中**使用了当时无法获得的信息**，导致回测结果虚高。

**常见错误**：

- 用当天收盘价计算信号，却用当天收盘价成交（应该用次日开盘价）
- 用未来数据填充缺失值
- 用全样本统计量（如全期均值）做标准化

### 🧮 常态计算方法

- 信号生成和交易执行**错开一天**
- 用 `shift(1)` 将信号延后一天
- 使用滚动窗口统计量，而非全样本统计量

### 🐍 Python 实现

python

```
# ❌ 错误：用当天信号当天成交
if df['Signal'].iloc[i] == 1:
    buy_price = df['close'].iloc[i]  # 前视偏差

# ✅ 正确：用昨天信号今天成交
if df['Signal'].iloc[i-1] == 1:
    buy_price = df['close'].iloc[i]

# ✅ 或者用 shift 显式延后
df['Signal_Lagged'] = df['Signal'].shift(1)
```



### ⚠️ 注意事项

- 项目中信号生成和交易执行在**同一循环**里，存在潜在的前视偏差
- 严格来说，应该用 `Signal.shift(1)` 作为交易信号
- 这是面试官**必问**的问题，需要能清楚解释

------

## 15. 过拟合（Overfitting）

### 📖 概念

过拟合指策略在**历史回测中表现很好**，但在**未来实盘中表现很差**。原因是策略过度适应了历史数据的噪声，而非捕捉到真实的规律。

**典型特征**：

- 在某个特定区间表现极好，换区间就失效
- 参数敏感性极高，微调参数结果差异巨大
- 交易次数过少，统计意义不足

### 🧮 常态检测方法

| 方法           | 说明                             |
| :------------- | :------------------------------- |
| **样本外检验** | 用一段数据调参，另一段数据验证   |
| **多区间验证** | 在多个时间区间测试，看是否稳定   |
| **多标的验证** | 在多只股票上测试，看是否普遍适用 |
| **参数敏感性** | 参数微调时结果是否平滑变化       |
| **交易次数**   | 样本量是否足够（通常 > 30 次）   |

### 🐍 Python 实现

python

```
# 多区间验证
for start, end in [('2020-01-01', '2023-01-01'), 
                   ('2023-01-01', '2026-01-01')]:
    stock_data = get_stock_data(symbol, start, end)
    perf = run_backtest(stock_data)
    print(f"{start}~{end}: 收益={perf['cumulative_return']*100:.2f}%")

# 多标的验证
for symbol in ['sh600519', 'sz000858', 'sh600036']:
    stock_data = get_stock_data(symbol, '2020-01-01', '2026-01-01')
    perf = run_backtest(stock_data)
    print(f"{symbol}: 收益={perf['cumulative_return']*100:.2f}%")
```



### ⚠️ 项目中的过拟合案例

- **ADX 过滤**：在 2025-2026 短区间改善收益，在 2020-2026 长区间恶化 → 过拟合
- **RSI < 60**：在消费股和新能源股上有效，在金融股和资源股上失效 → 行业依赖，非普遍规律
- **成交量过滤**：交易次数从 46 降到 3-13 次，样本量不足 → 统计意义有限

------

## 📚 附录：核心指标速查表

| 指标       | 公式                                   | 理想值 | Python 关键代码                                         |
| :--------- | :------------------------------------- | :----- | :------------------------------------------------------ |
| 累计收益率 | `(总资产/初始资金) - 1`                | > 0    | `df['Total Assets'] / initial_cash - 1`                 |
| 夏普比率   | `(年化收益 - 无风险利率) / 年化波动率` | > 1    | `daily_ret.mean()*252 / (daily_ret.std()*np.sqrt(252))` |
| 最大回撤   | `min((总资产 - 历史最高) / 历史最高)`  | > -20% | `drawdown_pct.min()`                                    |
| 胜率       | `盈利交易数 / 总交易数`                | > 50%  | `win_count / pair_count`                                |
| 盈亏比     | `总盈利 / 总亏损`                      | > 1.5  | `total_win / total_loss`                                |
| ADX        | `DX.ewm(alpha=1/14).mean()`            | > 25   | `df['DX'].ewm(alpha=1/14, adjust=False).mean()`         |
| RSI        | `100 - 100/(1+RS)`                     | 30~70  | `100 - (100 / (1 + df['RS']))`                          |

------

## 🔗 参考资料

- Welles Wilder, *New Concepts in Technical Trading Systems*（ADX/RSI 原始文献）
- Ernest Chan, *Quantitative Trading*（量化交易入门）
- 项目中 `aks_use_entire.py` 完整代码

------

> **免责声明**：本文档仅用于技术学习与策略研究，不构成任何投资建议。历史回测表现不代表未来收益。
