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
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

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
    We can now pass in a timeframe and limit to change sdz easily

    out puts a df with supply and demand zones for each time frame
    # this is supply zone n demand zone ranges
    # row 0 is the CLOSE, row 1 is the WICK (high/low)
    # and the supply/demand zone is inbetween the two
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

    return sd_df

async def limit_order(drift_client, symbol, order_params):
    order_ix = None
    if order_params.direction == PositionDirection.Long():
        order_ix = drift_client.get_place_perp_order_ix(order_params, 10)
    elif order_params.direction == PositionDirection.Short():
        order_ix = drift_client.get_place_perp_order_ix(order_params, 10)

    order_result = await drift_client.send_ix(order_ix)

    if order_params.direction == PositionDirection.Long():
        print(f"limit BUY order placed, resting: {order_result}")
    else:
        print(f"limit SELL order placed, resting: {order_result}")

    return order_result

async def get_position(drift_client, symbol):
    user_state = await drift_client.get_user_state()

    positions = []
    in_pos = False
    size = 0
    entry_px = 0
    pnl_perc = 0
    long = None

    for position in user_state.positions:
        if position.market.symbol == symbol:
            positions.append(position)
            in_pos = True
            size = position.base_asset_amount
            entry_px = position.entry_price
            pnl_perc = position.unrealized_pnl_percentage * 100
            long = position.base_asset_amount > 0

    return positions, in_pos, size, symbol, entry_px, pnl_perc, long

async def cancel_all_orders(drift_client):
    orders = await drift_client.get_open_orders()
    print(orders)
    print('above are the open orders... need to cancel any...')
    for order in orders:
        print(f"cancelling order {order}")
        await drift_client.cancel_order(order.order_id)

async def kill_switch(drift_client, symbol):
    positions, im_in_pos, pos_size, pos_sym, entry_px, pnl_perc, long = await get_position(drift_client, symbol)

    while im_in_pos:
        await cancel_all_orders(drift_client)

        orderbook = await drift_client.get_orderbook(symbol)
        ask = orderbook.asks[0].price
        bid = orderbook.bids[0].price

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
    env = "mainnet"
    market_name = "SOL-PERP"

    keypath = os.environ.get("ANCHOR_WALLET")
    with open(os.path.expanduser(keypath), "r") as f:
        secret = json.load(f)
    kp = Keypair.from_bytes(bytes(secret))
    print("using public key:", kp.pubkey())

    wallet = Wallet(kp)

    url = "https://solana-api.projectserum.com"
    connection = AsyncClient(url)

    drift_client = DriftClient(
        connection,
        wallet,
        str(env),
        account_subscription=AccountSubscriptionConfig("polling"),
    )

    await drift_client.add_user(10)

    await bot(drift_client)
    schedule.every(15).seconds.do(bot, drift_client)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print('+++++ maybe an internet problem.. code failed. sleeping 10')
            print(e)
            time.sleep(10)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())