'''
Drift Protocol connection and Supply Demand Zone Algo
'''
import os
import json
import time
import ccxt
import pandas as pd
import datetime
import schedule
import requests

from anchorpy import Wallet
from solders.keypair import Keypair # type: ignore
from solders.pubkey import Pubkey # type: ignore
from solana.rpc.async_api import AsyncClient
from driftpy.math.amm import calculate_bid_ask_price
from driftpy.math.market import (calculate_bid_price, calculate_ask_price)
#from driftpy.keypair import load_keypair

from driftpy.account_subscription_config import AccountSubscriptionConfig
from driftpy.constants.config import configs
from driftpy.types import (
    MarketType,
    OrderType,
    OrderParams,
    PositionDirection,
    OrderTriggerCondition,
    PostOnlyParams,
)
from driftpy.drift_client import DriftClient
from driftpy.constants.numeric_constants import BASE_PRECISION, PRICE_PRECISION
from driftpy.math.spot_position import (
    get_worst_case_token_amounts,
    is_spot_position_available,
)
from driftpy.math.perp_position import (
    calculate_position_pnl,
    calculate_entry_price,
    calculate_base_asset_value,
    is_available
)


#to-do add leverage later
symbol = 'SOL'
timeframe = '1h'  # for sdz zone
limit = 300  # for sdz
max_loss = -3
target = 12
size = 0.25

binance_symbol = symbol + '/USD'
print(binance_symbol)

def get_ohlcv(binance_symbol, timeframe='1h', limit=100):
    coinbase = ccxt.coinbasepro()
    
    ohlcv = coinbase.fetch_ohlcv(binance_symbol, timeframe, limit)
    
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    df = df.tail(limit)

    df['support'] = df[:-2]['close'].min()
    df['resis'] = df[:-2]['close'].max()    

    return df

def supply_demand_zones(symbol, timeframe, limit):
    '''
    We can now pass in a timeframe and limit to change supply/demand zone easily

    outputs a data frame with supply and demand zones for each time frame
    # this is supply zone and demand zone ranges
    # row 0 is the CLOSE, row 1 is the WICK (high/low)
    # and the supply/demand zone is in between the two
    '''

    print('starting supply and demand zone calculations..')

    # get OHLCV data     
    sd_df = pd.DataFrame() # supply and demand zone dataframe 

    df = get_ohlcv(binance_symbol, timeframe, limit)
    print(df)
    
    supp_1h = df.iloc[-1]['support']
    resis_1h = df.iloc[-1]['resis']

    df['supp_lo'] = df[:-2]['low'].min()
    supp_lo_1h = df.iloc[-1]['supp_lo']

    df['res_hi'] = df[:-2]['high'].max()
    res_hi_1h = df.iloc[-1]['res_hi']

    sd_df['1h_dz'] = [supp_lo_1h, supp_1h]
    sd_df['1h_sz'] = [res_hi_1h, resis_1h]

    return sd_df # this is a df where the zone is indicated per timeframe
                # and range is between row 0 and 1

async def limit_order(drift_client, symbol, order_params):
    order_ix = None
    if order_params.direction == PositionDirection.Long():
        #order_ix = drift_client.place_perp_order_ix(order_params)
        order_tx_sig = await drift_client.place_perp_order_ix(order_params)
    elif order_params.direction == PositionDirection.Short():
        #order_ix = drift_client.place_perp_order_ix(order_params)
        order_tx_sig = await drift_client.place_perp_order_ix(order_params)

    #order_result = await drift_client.send_ixs(order_ix)

    if order_params.direction == PositionDirection.Long():
        print(f"limit BUY order placed, order tx: {order_tx_sig}")
    else:
        print(f"limit SELL order placed, order tx: {order_tx_sig}")

    return order_tx_sig

async def get_position(drift_client, _market_index):
    #user_account = drift_client.get_user_account()
    user = drift_client.get_user()
    user_account = user.get_user_account()
    oracle_price_data = drift_client.get_oracle_price_data_for_perp_market(_market_index)

    in_pos = False
    size = 0
    entry_px = 0
    pnl_perc = 0
    is_long = None

    position = user.get_perp_position(_market_index)
    entry_px = calculate_entry_price(position)
    in_pos = True if position != None else False
    market = drift_client.get_perp_market_account(_market_index)
    #pnl_perc = calculate_position_pnl(market, position, oracle_price_data)
    pnl_perc = user.get_unrealized_pnl(_market_index)
    base_asset_amount = position.base_asset_amount if position is not None else 0

    is_long = base_asset_amount > 0
    size = base_asset_amount
    #is_short = base_asset_amount < 0

    return position, in_pos, size, entry_px, pnl_perc, is_long

async def cancel_all_orders(drift_client):
    orders = await drift_client.get_open_orders()
    print(orders)
    print('above are the open orders... need to cancel any...')
    for order in orders:
        print(f"cancelling order {order}")
        await drift_client.cancel_order(order.order_id)

async def kill_switch(drift_client, market_index):
    oracle_price_data = drift_client.get_oracle_price_data_for_perp_market(market_index)
    positions, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = await get_position(drift_client, symbol)

    while im_in_pos:
        await cancel_all_orders(drift_client)

        market = drift_client.get_perp_market_account(market_index)
        bid = calculate_bid_price(market, oracle_price_data)
        ask = calculate_ask_price(market, oracle_price_data)

        pos_size = abs(pos_size)

        if long:
            order_params = OrderParams(
                order_type=OrderType.Limit(),
                market_type=MarketType.Perp(),
                direction=PositionDirection.Short(),
                base_asset_amount=pos_size,
                price=ask,
            )
            await limit_order(drift_client, symbol, order_params)
            print('kill switch - SELL TO CLOSE SUBMITTED ')
            time.sleep(7)
        else:
            order_params = OrderParams(
                order_type=OrderType.Limit(),
                market_type=MarketType.Perp(),
                direction=PositionDirection.Long(),
                base_asset_amount=pos_size,
                price=bid,
            )
            await limit_order(drift_client, symbol, order_params)
            print('kill switch - BUY TO CLOSE SUBMITTED ')
            time.sleep(7)
        
        positions, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = await get_position(drift_client, symbol)

    print('position successfully closed in kill switch')

async def pnl_close(drift_client, symbol):
    print('entering pnl close')
    positions, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = await get_position(drift_client, symbol)
    if pnl_perc > target:
        print(f'pnl gain is {pnl_perc} and target is {target}... closing position WIN')
        await kill_switch(drift_client, pos_sym)
    elif pnl_perc <= max_loss:
        print(f'pnl loss is {pnl_perc} and max loss is {max_loss}... closing position LOSS')
        await kill_switch(drift_client, pos_sym)
    else:
        print(f'pnl loss is {pnl_perc} and max loss is {max_loss} and target {target}... not closing position')
    print('finished with pnl close')

async def bot(drift_client):
    sdz = supply_demand_zones(symbol, timeframe, limit)
    print(sdz)

    sz_1hr = sdz['1h_sz']
    sz_1hr_0 = sz_1hr.iloc[0]
    sz_1hr_1 = sz_1hr.iloc[-1]

    dz_1hr = sdz['1h_dz']
    dz_1hr_0 = dz_1hr.iloc[0]
    dz_1hr_1 = dz_1hr.iloc[-1]

    buy1 = max(dz_1hr_0, dz_1hr_1)
    buy2 = (dz_1hr_0 + dz_1hr_1) / 2

    sell1 = min(sz_1hr_0, sz_1hr_1)
    sell2 = (sz_1hr_0 + sz_1hr_1) / 2

    positions, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = await get_position(drift_client, symbol)

    orders = await drift_client.get_open_orders()
    open_order_prices = [order.price for order in orders]
    print(open_order_prices)

    if buy2 and sell2 in open_order_prices:
        new_orders_needed = False
        print('buy2 and sell2 in open orders')
    else:
        new_orders_needed = True
        print('no open orders')

    if not im_in_pos and new_orders_needed:
        print('not in position.. setting orders...')
        await cancel_all_orders(drift_client)

        buy_order_params = OrderParams(
            order_type=OrderType.Limit(),
            market_type=MarketType.Perp(),
            direction=PositionDirection.Long(),
            base_asset_amount=size,
            price=buy2,
        )
        await limit_order(drift_client, symbol, buy_order_params)

        sell_order_params = OrderParams(
            order_type=OrderType.Limit(),
            market_type=MarketType.Perp(),
            direction=PositionDirection.Short(),
            base_asset_amount=size,
            price=sell2,
        )
        await limit_order(drift_client, symbol, sell_order_params)

    elif im_in_pos:
        print('we are in position.. checking PNL loss')
        await pnl_close(drift_client, symbol)
    else:
        print('orders already set... chilling')

async def main():
    env = "devnet"
    market_name = "SOL-PERP"

    keypath = os.environ.get("ANCHOR_WALLET")
    with open(os.path.expanduser(keypath), "r") as f:
        secret = json.load(f)

    kp = Keypair.from_bytes(bytes(secret))
    #kp = load_keypair(f)  
    print("using public key:", kp.pubkey())

    wallet = Wallet(kp)

    url = "https://solana-api.projectserum.com"
    connection = AsyncClient(url)

    drift_client = DriftClient(
        connection,
        wallet,
        str(env),
        account_subscription=AccountSubscriptionConfig("demo"),
    )

    await drift_client.initialize_user()

    while True:
        try:
            await bot(drift_client)
            await asyncio.sleep(15)
        except Exception as e:
            print('+++++ maybe an internet problem.. code failed. sleeping 10')
            print(e)
            await asyncio.sleep(10)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())