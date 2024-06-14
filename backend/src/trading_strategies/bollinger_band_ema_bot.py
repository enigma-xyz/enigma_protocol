import os
import json
import asyncio
import logging
import pandas as pd
import pandas_ta as pd_ta
from anchorpy import Wallet
from solders.keypair import Keypair  # type: ignore
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

symbol = '1MBONK-PERP'
timeperiod = 20
ema_period = 20
take_profit = 1.1
stop_loss = 0.95
size = 1

secret_key = os.environ.get("DRIFT_WALLET_PRIVATE_KEY")

async def get_position(drift_client, market_index):
    user = drift_client.get_user()
    positions = [position for position in user.positions if position.market_index == market_index]
    return positions[0] if positions else None

async def limit_order(drift_client, market_index, is_buy, sz, limit_px, reduce_only=False):
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

async def bot(drift_client, market_index):
    market = drift_client.get_market(market_index)
    close_price = float(market.oracle_price)

    bbands = pd_ta.bbands(close_price, timeperiod=timeperiod, nbdevup=2, nbdevdn=2)
    upper_band = bbands['BBU_' + str(timeperiod)].iloc[-1]
    lower_band = bbands['BBL_' + str(timeperiod)].iloc[-1]

    ema = pd_ta.ema(close_price, timeperiod=ema_period)
    ema_value = ema.iloc[-1]

    position = await get_position(drift_client, market_index)
    im_in_pos = position is not None

    if (close_price > upper_band) or (ema_value > close_price):
        if not im_in_pos:
            logger.info('Buy signal triggered')
            await limit_order(drift_client, market_index, True, size, close_price)
        else:
            logger.info('Already in position, skipping buy signal')

    elif close_price < ema_value:
        if im_in_pos:
            logger.info('Sell signal triggered')
            await kill_switch(drift_client, market_index)
            await limit_order(drift_client, market_index, False, size * 2, close_price)
        else:
            logger.info('No position to sell')

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
            await asyncio.sleep(60)  # Run the bot every minute
        except Exception as e:
            logger.error(f"Error in bot: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())