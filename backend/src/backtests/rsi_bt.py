from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import pandas as pd
import pandas_ta as pd_ta
import ta

class RSI_Trend_Strategy(Strategy):
    # Define the parameters for optimization as class variables
    EMA_SHORT = 13
    EMA_MID = 21
    EMA_LONG = 55

    def init(self):
        self.ema_short = self.I(pd_ta.ema, self.data.Close, length=self.EMA_SHORT)
        self.ema_mid = self.I(pd_ta.ema, self.data.Close, length=self.EMA_MID)
        self.ema_long = self.I(pd_ta.ema, self.data.Close, length=self.EMA_LONG)
        self.macd_line, _, self.macd_hist = self.I(pd_ta.macd, self.data.Close, fast=8, slow=21, signal=8)
        self.rsi_short = self.I(pd_ta.rsi, self.data.Close, length=8)

    def next(self):
        if crossover(self.data.Close, self.ema_short) > 0 and \
            crossover(self.data.Close, self.ema_mid) > 0 and \
            crossover(self.ema_short, self.ema_long) > 0 and \
            self.rsi_short[-1] > 0 and \
            self.rsi_short[-1] < 58:
            self.buy()
        elif crossover(self.ema_short, self.data.Close) > 0 and \
            crossover(self.ema_mid, self.data.Close) > 0 and \
            crossover(self.ema_long, self.data.Close) > 0 and \
            self.rsi_short[-1] < 0 and \
            self.rsi_short[-1] > 50:
            self.sell()

data = pd.read_csv('/users/tc/Dropbox/dev/github/open-AI-Assistant/final_backtests/BTC-USD-15m-2019-1-01T00_00.csv')
# drop the last column if it's empty
data = data.iloc[:, :-1]

# Clean up the column names to capitalize the first letter of each word
data.columns = data.columns.str.title().str.title()

# Convert the "Datetime" column to datetime format and set it as the index
data['Datetime'] = pd.to_datetime(data['Datetime'])
data.set_index('Datetime', inplace=True)

# Initialize and run the backtest with parameter optimization
bt = Backtest(data, RSI_Trend_Strategy, cash=100000, commission=.002)

optimization_results = bt.optimize(
    SMA_Short=range(5, 20, 2),  # Testing different EMA short periods
    SMA_Long=range(10, 30, 2),  # Testing different EMA long periods
    EMA_Low=range(45, 70, 5),  # Testing different EMA low periods
    return_heatmap=True, maximize='Equity Final [$]'
)

print(optimization_results)