import os
import json
import time
import asyncio
import logging
import pandas as pd
from datetime import datetime, timedelta
import ccxt
import pandas_ta as ta
from anchorpy import Wallet
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from driftpy.types import (
    MarketType,
    OrderType,
    OrderParams,
    PositionDirection,
)
from driftpy.drift_client import DriftClient
from driftpy.math.perp_position import calculate_entry_price
from driftpy.account_subscription_config import AccountSubscriptionConfig
from driftpy.constants.config import configs

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

symbol = 'SOL-PERP'
timeframe = '15m'
sma_window = 20
lookback_days = 1
size = 1
target = 5
max_loss = -10
leverage = 3
max_positions = 1

secret_key = os.environ.get("DRIFT_WALLET_PRIVATE_KEY")

async def get_position_andmaxpos(drift_client, market_index, max_positions):
    user = drift_client.get_user()
    positions = []
    open_positions = []

    for position in user.positions:
        if position.market_index == market_index and position.base_asset_amount != 0:
            positions.append(position)
            open_positions.append(position.market)

    num_of_pos = len(open_positions)

    if len(open_positions) > max_positions:
        logger.info(f'We are in {len(open_positions)} positions and max pos is {max_positions}... closing positions')
        for position in open_positions:
             await kill_switch(drift_client, position.market_index)
    else:
        logger.info(f'We are in {len(open_positions)} positions and max pos is {max_positions}... not closing positions')

    if positions:
        position = positions[0]
        in_pos = True
        size = position.base_asset_amount
        pos_sym = position.market
        entry_px = calculate_entry_price(position)
        pnl_perc = position.unrealized_pnl_percentage * 100
        long = size > 0
    else:
        in_pos = False
        size = 0
        pos_sym = None
        entry_px = 0
        pnl_perc = 0
        long = None

    return positions, in_pos, size, pos_sym, entry_px, pnl_perc, long, num_of_pos

async def adjust_leverage_size_signal(drift_client, market_index, leverage):
    user = drift_client.get_user()
    acct_value = float(user.collateral)
    acct_val95 = acct_value * 0.95

    await drift_client.set_leverage(market_index, leverage)

    market = drift_client.get_market(market_index)
    price = float(market.oracle_price)

    size = (acct_val95 / price) * leverage
    size = round(size, market.base_precision)

    return leverage, size

async def cancel_all_orders(drift_client):
    user = drift_client.get_user()
    orders = await user.get_open_orders()
    logger.info(f"Open orders: {orders}")
    logger.info('Canceling open orders...')
    for order in orders:
        logger.info(f"Cancelling order {order}")
        await drift_client.cancel_order(order.order_id)

async def limit_order(drift_client, market_index, is_buy, sz, limit_px, reduce_only):
    order_params = OrderParams(
        order_type=OrderType.LIMIT,
        market_type=MarketType.PERP,
        direction=PositionDirection.LONG if is_buy else PositionDirection.SHORT,
        base_asset_amount=sz,
        price=limit_px,
        market_index=market_index,
        reduce_only=reduce_only,
    )
    order_result = await drift_client.place_order(order_params)

    if is_buy:
        logger.info(f"Limit BUY order placed, resting: {order_result}")
    else:
        logger.info(f"Limit SELL order placed, resting: {order_result}")

    return order_result

async def kill_switch(drift_client, market_index):
    position = await get_position(drift_client, market_index)
    im_in_pos = position is not None

    while im_in_pos:
        await cancel_all_orders(drift_client)

        pos_size = abs(position.base_asset_amount)
        long = position.base_asset_amount > 0

        order_params = OrderParams(
            order_type=OrderType.MARKET,
            market_type=MarketType.PERP,
            direction=PositionDirection.SHORT if long else PositionDirection.LONG,
            base_asset_amount=pos_size,
            market_index=market_index,
        )
        await drift_client.place_order(order_params)

        if long:
            logger.info('Kill switch - SELL TO CLOSE SUBMITTED')
        else:
            logger.info('Kill switch - BUY TO CLOSE SUBMITTED')

        await asyncio.sleep(5)
        position = await get_position(drift_client, market_index)
        im_in_pos = position is not None

    logger.info('Position successfully closed in kill switch')

async def pnl_close(drift_client, market_index, target, max_loss):
    logger.info('Entering PNL close')
    position = await get_position(drift_client, market_index)

    if position:
        pnl_perc = position.unrealized_pnl_percentage * 100

        if pnl_perc > target:
            logger.info(f'PNL gain is {pnl_perc}% and target is {target}%... closing position WIN')
            await kill_switch(drift_client, market_index)
        elif pnl_perc <= max_loss:
            logger.info(f'PNL loss is {pnl_perc}% and max loss is {max_loss}%... closing position LOSS')
            await kill_switch(drift_client, market_index)
        else:
            logger.info(f'PNL is {pnl_perc}% and within accepted range... not closing position')

    logger.info('Finished PNL close')

async def get_position(drift_client, market_index):
    user = drift_client.get_user()
    positions = [position for position in user.positions if position.market_index == market_index]
    return positions[0] if positions else None

def fetch_ohlcv(exchange, symbol, timeframe, limit):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def calculate_bollinger_bands(df, length=20, std_dev=2):
    bollinger_bands = ta.bbands(df['close'], length=length, std=std_dev)
    bollinger_bands = bollinger_bands.iloc[:, [0, 1, 2]]
    bollinger_bands.columns = ['BBL', 'BBM', 'BBU']
    df = pd.concat([df, bollinger_bands], axis=1)
    df['BandWidth'] = df['BBU'] - df['BBL']
    tight_threshold = df['BandWidth'].quantile(0.2)
    wide_threshold = df['BandWidth'].quantile(0.8)
    current_band_width = df['BandWidth'].iloc[-1]
    tight = current_band_width <= tight_threshold
    wide = current_band_width >= wide_threshold
    return df, tight, wide

async def bot(drift_client, market_index):
    exchange = ccxt.coinbasepro()
    positions, im_in_pos, mypos_size, pos_sym, entry_px, pnl_perc, long, num_of_pos = await get_position_andmaxpos(drift_client, market_index, max_positions)

    logger.info(f'These are positions for {symbol}: {positions}')

    lev, pos_size = await adjust_leverage_size_signal(drift_client, market_index, leverage)
    pos_size /= 2

    if im_in_pos:
        await cancel_all_orders(drift_client)
        logger.info('In position, so check PNL close')
        await pnl_close(drift_client, market_index, target, max_loss)
    else:
        logger.info('Not in position, so no PNL close')

    market = drift_client.get_market(market_index)
    bid = float(market.bids[0].price)
    ask = float(market.asks[0].price)

    logger.info(f'Ask: {ask}, Bid: {bid}')

    bid11 = float(market.bids[10].price)
    ask11 = float(market.asks[10].price)

    logger.info(f'Ask11: {ask11}, Bid11: {bid11}')

    df = fetch_ohlcv(exchange, 'BTC/USD', '1m', 500)
    bbdf, bollinger_bands_tight, _ = calculate_bollinger_bands(df)

    logger.info(f'Bollinger bands are tight: {bollinger_bands_tight}')

    if not im_in_pos and bollinger_bands_tight:
        logger.info('Bollinger bands are tight and we don\'t have a position, so entering')
        logger.info(f'Not in position, we are quoting a sell @ {ask} and buy @ {bid}')
        await cancel_all_orders(drift_client)
        logger.info('Just canceled all orders')

        await limit_order(drift_client, market_index, True, pos_size, bid11, False)
        logger.info(f'Just placed a BUY order for {pos_size} at {bid11}')

        await limit_order(drift_client, market_index, False, pos_size, ask11, False)
        logger.info(f'Just placed a SELL order for {pos_size} at {ask11}')

    elif not bollinger_bands_tight:
        await cancel_all_orders(drift_client)
        for position in positions:
            await kill_switch(drift_client, position.market_index)
    else:
        logger.info(f'Our position is {im_in_pos}, bollinger bands may not be tight')

async def main():
    env = "mainnet"
    keypath = os.environ.get("DRIFT_WALLET_PRIVATE_KEY")
    with open(os.path.expanduser(keypath), "r") as f:
        secret = json.load(f)

    kp = Keypair.from_bytes(bytes(secret))
    logger.info(f"Using public key: {kp.pubkey()}")

    wallet = Wallet(kp)

    url = configs[env].rpc_url
    connection = AsyncClient(url)

    drift_client = DriftClient(
        connection,
        wallet,
        env,
        account_subscription=AccountSubscriptionConfig(),
    )

    await drift_client.initialize()

    market_index = await drift_client.get_market_index_by_symbol(symbol)

    while True:
        try:
            await bot(drift_client, market_index)
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Error in bot: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())