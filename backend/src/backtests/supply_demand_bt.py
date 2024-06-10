from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import ccxt
import warnings
warnings.filterwarnings('ignore')

class SupplyDemandZoneStrategy(Strategy):
    timeframe = '1h'
    limit = 300
    max_loss = -0.03
    target = 0.12
    size = 0.25

    def init(self):
        self.exchange = ccxt.coinbase()
        self.symbol = 'SOL/USD'
        self.df = self.fetch_ohlcv()
        self.zones = self.supply_demand_zones()
        self.buy_price = (self.zones['1h_dz'][0] + self.zones['1h_dz'][1]) / 2
        self.sell_price = (self.zones['1h_sz'][0] + self.zones['1h_sz'][1]) / 2

    def fetch_ohlcv(self):
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=self.limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def supply_demand_zones(self):
        df = self.df.copy()
        df['support'] = df[:-2]['close'].min()
        df['resis'] = df[:-2]['close'].max()
        df['supp_lo'] = df[:-2]['low'].min()
        df['res_hi'] = df[:-2]['high'].max()
        sd_df = pd.DataFrame()
        sd_df['1h_dz'] = [df.iloc[-1]['supp_lo'], df.iloc[-1]['support']]
        sd_df['1h_sz'] = [df.iloc[-1]['res_hi'], df.iloc[-1]['resis']]
        return sd_df

    def next(self):
        price = self.data.close[-1]

        if not self.position:
            if price <= self.buy_price:
                self.buy(size=self.size)
            elif price >= self.sell_price:
                self.sell(size=self.size)
        else:
            if self.position.is_long:
                if price <= self.position.entry_price * (1 + self.max_loss):
                    self.position.close()
                elif price >= self.position.entry_price * (1 + self.target):
                    self.position.close()
            else:  # Short position
                if price >= self.position.entry_price * (1 + abs(self.max_loss)):
                    self.position.close()
                elif price <= self.position.entry_price * (1 - self.target):
                    self.position.close()

data = pd.read_csv('SOL-USD_1h_100.csv')
# drop the last column if it's empty
data = data.iloc[:, :-1]


# Clean up the column names to capitalize the first letter of each word
data.columns = data.columns.str.title().str.title()

# Convert the "Datetime" column to datetime format and set it as the index
data['Datetime'] = pd.to_datetime(data['Datetime'])
data.set_index('Datetime', inplace=True)

bt = Backtest(data, SupplyDemandZoneStrategy, cash=10000, commission=0.002, exclusive_orders=True)

stats = bt.run()
print(stats)

bt.plot()