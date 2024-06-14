'''
this is the og funding script with long and short

Start                     2023-08-04 16:50:51                        
End                       2023-09-21 07:30:42
Duration                     47 days 14:39:51
Exposure Time [%]                   70.982392
Equity Final [$]                  1325498.376
Equity Peak [$]                   1340786.376
Return [%]                          32.549838
Buy & Hold Return [%]               -7.520332
Return (Ann.) [%]                  781.366024
Volatility (Ann.) [%]              546.311679
Sharpe Ratio                         1.430257
Sortino Ratio                       91.397066
Calmar Ratio                       160.837257
Max. Drawdown [%]                   -4.858116
Avg. Drawdown [%]                   -0.485489
Max. Drawdown Duration       11 days 15:15:01
Avg. Drawdown Duration        0 days 10:51:41
# Trades                                    5
Win Rate [%]                             80.0
Best Trade [%]                      14.091876
Worst Trade [%]                     -0.258446
Avg. Trade [%]                       5.877773
Max. Trade Duration          13 days 00:49:51
Avg. Trade Duration           6 days 10:33:59
Profit Factor                      116.639755
Expectancy [%]                       5.977334
SQN                                  2.880141
_strategy                 FundingRateStrat...
_equity_curve                             ...
_trades                      Size  EntryBa...
dtype: object
funding_rate_threshold  short_funding_rate_threshold  take_profit  max_loss
-43                     32                            0.06         0.08        1325498.376
-41                     32                            0.06         0.05        1325498.376
-48                     32                            0.06         0.05        1325498.376
'''


from backtesting import Backtest, Strategy
import pandas as pd
# hide warnings
import warnings
warnings.filterwarnings('ignore')

class FundingRateStrategy(Strategy):
    funding_rate_threshold = -43
    short_funding_rate_threshold = 32  # New variable for shorting based on funding rate
    take_profit = 0.05
    max_loss = 0.03
    
    def init(self):
        self.buy_signal = self.I(lambda x: x < self.funding_rate_threshold, self.data['funding rate'])
        self.short_signal = self.I(lambda x: x > self.short_funding_rate_threshold, self.data['funding rate'])

    def next(self):
        price = self.data.Close[-1]
        tp_price_long = price * (1 + self.take_profit)
        sl_price_long = price * (1 - self.max_loss)
        
        tp_price_short = price * (1 - self.take_profit)
        sl_price_short = price * (1 + self.max_loss)

        # Long logic
        if self.buy_signal[-1] and not self.position:
            self.buy(sl=sl_price_long, tp=tp_price_long)
        # Short logic
        elif self.short_signal[-1] and not self.position:
            self.sell(sl=sl_price_short, tp=tp_price_short)


data = pd.read_csv('funding_rates_data.csv')
data['Datetime'] = pd.to_datetime(data['datetime'], format='%m-%d-%y %H:%M:%S')

# Split the DataFrame based on the 'symbol' column and make a copy
btc_data = data[(data['symbol'] == 'BTC-USD-dydx') | (data['symbol'] == 'BTC-USD')].copy()

# make fake ohlc based off bid/ask
btc_data['Open'] = btc_data['ask']
btc_data['High'] = btc_data['ask']
btc_data['Low'] = btc_data['bid']
btc_data['Close'] = btc_data['ask']

btc_data.set_index('Datetime', inplace=True)

# Filter rows to keep only those occurring at 5-minute intervals
btc_data = btc_data[btc_data.index.minute % 1 == 0]

# Ensure the DataFrame is sorted by datetime (important for backtesting)
btc_data = btc_data.sort_values(by='Datetime')


bt = Backtest(btc_data, FundingRateStrategy, cash=1000000, commission=.006)

#stats = bt.run()
stats, heatmap = bt.optimize(
    # funding_rate_threshold=range(-50, -40, 1),
    # short_funding_rate_threshold=range(24, 50, 2),  # Optimization range for short threshold
    take_profit=[i/100 for i in range(6, 15)],
    max_loss=[i/100 for i in range(8,15)],
    maximize='Equity Final [$]',
    return_heatmap=True)

print(stats)
print(heatmap.sort_values().iloc[-3:])
bt.plot()










# from backtesting import Backtest, Strategy
# import pandas as pd
# import numpy as np

# class FundingRateStrategy(Strategy):
#     funding_rate_threshold_long = -0.02
#     funding_rate_threshold_short = 0.02
#     stop_loss = 0.01
#     take_profit = 0.03
    
#     def init(self):
#         self.funding_rates = self.I(lambda: self.data.fundingRate, name='funding_rate')
#         self.cumulative_funding_rate_long = self.I(lambda: self.data.cumulativeFundingRateLong, name='cumulative_funding_rate_long')
#         self.cumulative_funding_rate_short = self.I(lambda: self.data.cumulativeFundingRateShort, name='cumulative_funding_rate_short')
    
#     def next(self):
#         if not self.position:
#             if self.funding_rates[-1] < self.funding_rate_threshold_long:
#                 self.buy(sl=self.data.markPriceTwap[-1] * (1 - self.stop_loss), tp=self.data.markPriceTwap[-1] * (1 + self.take_profit))
#             elif self.funding_rates[-1] > self.funding_rate_threshold_short:
#                 self.sell(sl=self.data.markPriceTwap[-1] * (1 + self.stop_loss), tp=self.data.markPriceTwap[-1] * (1 - self.take_profit))
#         else:
#             if self.position.is_long:
#                 if self.cumulative_funding_rate_long[-1] > 0:
#                     self.position.close()
#             elif self.position.is_short:
#                 if self.cumulative_funding_rate_short[-1] < 0:
#                     self.position.close()

# data = pd.read_csv('data.csv', dtype={
#     'ts': int,
#     'markPriceTwap': float,
#     'baseAssetAmountWithAmm': float,
#     'fundingRate': float,
#     'cumulativeFundingRateLong': float,
#     'cumulativeFundingRateShort': float
# })

# # Convert 'ts' column to datetime
# data['ts'] = pd.to_datetime(data['ts'], unit='s')
# data.set_index('ts', inplace=True)

# # Create a new DataFrame with the required columns
# ohlcv_data = pd.DataFrame({
#     'Open': data['markPriceTwap'],
#     'High': data['markPriceTwap'],
#     'Low': data['markPriceTwap'],
#     'Close': data['markPriceTwap'],
#     'Volume': data['baseAssetAmountWithAmm']
# })

# # Merge the new DataFrame with the original data
# data = pd.concat([ohlcv_data, data], axis=1)

# # Initialize and run the Backtest
# bt = Backtest(data, FundingRateStrategy, cash=10000, commission=0.002, exclusive_orders=True)
# stats = bt.run()
# print(stats)

# # Optimize strategy parameters
# # stats_opt = bt.optimize(
# #     funding_rate_threshold_long=np.arange(-0.05, 0, 0.01),
# #     funding_rate_threshold_short=np.arange(0, 0.05, 0.01),
# #     stop_loss=np.arange(0.005, 0.03, 0.005),
# #     take_profit=np.arange(0.01, 0.06, 0.01),
# #     maximize='Equity Final [$]',
# #     constraint=lambda param: param.take_profit > param.stop_loss
# # )

# # print(stats_opt)

# # bt.plot()