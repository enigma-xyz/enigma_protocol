from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import pandas as pd

class VolumeSpikeStrategy(Strategy):
    volume_spike_ratio = 2.0  # 200% increase
    tp_ratio = 0.04  # 4% target profit
    sl_ratio = 0.03  # 3% stop loss

    def init(self):
        # Calculate the moving average of the volume for comparison
        self.avg_volume = self.I(SMA, self.data.Volume, 20)

    def next(self):
        # Log the current volume and the average volume
        print(f"Date: {self.data.index[-1]}, Current Volume: {self.data.Volume[-1]}")

        # Check for a volume spike
        if self.data.Volume[-1] > self.volume_spike_ratio * self.avg_volume[-1]:
            print(f"Volume spike detected on {self.data.index[-1]}")

            # Calculate stop loss and take profit prices
            stop_loss = self.data.Close[-1] * (1 - self.sl_ratio)
            take_profit = self.data.Close[-1] * (1 + self.tp_ratio)

            # Log the SL and TP
            print(f"Executing Buy: SL at {stop_loss}, TP at {take_profit}")
        
                    # Log the SL and TP
            print(f"Executing Buy: SL at {stop_loss}, TP at {take_profit}")

            # Enter a long position with the specified SL and TP
            self.buy(sl=stop_loss, tp=take_profit)

# Load the data
data_path = '/Users/tc/Dropbox/dev/github/backtests-for-bootcamp/ETH-USD-15m-2021.csv'
data = pd.read_csv(data_path, index_col='datetime', parse_dates=True)

# send me SYMBOL data since YEAR in TIMEFRAME timeframe
# If there is an extra unnamed or unnecessary column, you can drop it
data = data.iloc[:, :5]

# Ensure the DataFrame contains columns 'Open', 'High', 'Low', 'Close', 'Volume'
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Create and configure the backtest
bt = Backtest(data, VolumeSpikeStrategy, cash=100000, commission=0.002)

# Create and configure the backtest
bt = Backtest(data, VolumeSpikeStrategy, cash=100000, commission=0.001)

# Optimization
optimization_results = bt.optimize(
    volume_spike_ratio=range(1, 5, 1),  # Testing different volume spikes
    tp_ratio=[x / 100 for x in range(3, 13)], # Testing TP ratios from 0.03 to 0.12
    sl_ratio=[x / 100 for x in range(3, 13)], # Testing SL ratios from 0.03 to 0.12
    maximize='Equity Final [$]'
)

# Print the optimization results
print(optimization_results)

# Print the best optimized values
print("Best Parameters:")

print("Volume Spike Ratio:", optimization_results._strategy.volume_spike_ratio)
print("Target Profit Ratio:", optimization_results._strategy.tp_ratio)

print("Stop Loss Ratio:", optimization_results._strategy.sl_ratio)
