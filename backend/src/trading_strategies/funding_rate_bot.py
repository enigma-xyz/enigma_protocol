import os
import json
import asyncio
import logging
import pandas as pd
from datetime import datetime
from anchorpy import Wallet
from solders.keypair import Keypair # type: ignore
from solana.rpc.async_api import AsyncClient
from driftpy.account_subscription_config import AccountSubscriptionConfig
from driftpy.types import (
    MarketType,
    OrderType,
    OrderParams,
    PositionDirection,
)
from driftpy.drift_client import DriftClient
from driftpy.math.perp_position import (
    calculate_entry_price,
)

# Explanation:

# 1. The bot strategy is implemented in the `FundingRateStrategy` class, which takes the Drift client, market name, funding rate thresholds, take profit, max loss, and position size as parameters.

# 2. The `get_position` method retrieves the current position details, including entry price, PNL percentage, and position size.

# 3. The `cancel_all_orders` method cancels all open orders.

# 4. The `limit_order` method places a limit order based on the provided order parameters.

# 5. The `kill_switch` method closes the current position by placing a market order in the opposite direction.

# 6. The `pnl_close` method checks the PNL percentage and triggers the kill switch if the take profit or max loss thresholds are reached.

# 7. The `bot` method is the main logic of the strategy. It retrieves the current funding rate and checks if there is an existing position. If there is no position and the funding rate is below the buy threshold or above the short threshold, it places a market order to enter a long or short position, respectively. If there is an existing position, it checks the PNL and triggers the `pnl_close` method.

# 8. The `main` function sets up the Drift client, initializes the strategy with the specified parameters, and runs the bot in an infinite loop, executing the strategy every minute.

# This bot strategy incorporates the funding rate signals from the backtest to make trading decisions using the Drift Protocol. It enters long positions when the funding rate is below the buy threshold and short positions when the funding rate is above the short threshold. The bot also manages position closing based on the take profit and max loss thresholds.

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FundingRateStrategy:
    def __init__(self, drift_client, market_name, funding_rate_threshold, short_funding_rate_threshold, take_profit, max_loss, size):
        self.drift_client = drift_client
        self.market_name = market_name
        self.funding_rate_threshold = funding_rate_threshold
        self.short_funding_rate_threshold = short_funding_rate_threshold
        self.take_profit = take_profit
        self.max_loss = max_loss
        self.size = size

    async def get_position(self, _market_index):
        user = self.drift_client.get_user()

        in_pos = False
        size = 0
        entry_px = 0
        pnl_perc = 0
        is_long = None

        position = user.get_perp_position(_market_index)
        entry_px = calculate_entry_price(position)
        in_pos = True if position is not None else False
        pnl_perc = user.get_unrealized_pnl(_market_index)
        base_asset_amount = position.base_asset_amount if position is not None else 0

        is_long = base_asset_amount > 0
        size = base_asset_amount

        return position, in_pos, size, entry_px, pnl_perc, is_long

    async def cancel_all_orders(self):
        user = self.drift_client.get_user()
        orders = await user.get_open_orders()
        logger.info(f"Open orders: {orders}")
        logger.info('Canceling open orders...')
        for order in orders:
            logger.info(f"Cancelling order {order}")
            await self.drift_client.cancel_order(order.order_id)

    async def limit_order(self, order_params):
        order_tx_sig = None
        try:
            order_tx_sig = await self.drift_client.place_perp_order_ix(order_params)
            if order_params.direction == PositionDirection.Long():
                logger.info(f"Limit BUY order placed, order tx: {order_tx_sig}")
            else:
                logger.info(f"Limit SELL order placed, order tx: {order_tx_sig}")
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")

        return order_tx_sig

    async def kill_switch(self, market_index, market_type):
        position, im_in_pos, pos_size, entry_px, pnl_perc, long = await self.get_position(market_index)

        while im_in_pos:
            await self.cancel_all_orders()

            pos_size = abs(pos_size)

            if long:
                order_params = OrderParams(
                    order_type=OrderType.Market(),
                    market_type=market_type,
                    direction=PositionDirection.Short(),
                    base_asset_amount=pos_size,
                    market_index=market_index
                )
                await self.limit_order(order_params)
                logger.info('Kill switch - SELL TO CLOSE SUBMITTED')
                await asyncio.sleep(7)
            else:
                order_params = OrderParams(
                    order_type=OrderType.Market(),
                    market_type=market_type,
                    direction=PositionDirection.Long(),
                    base_asset_amount=pos_size,
                    market_index=market_index
                )
                await self.limit_order(order_params)
                logger.info('Kill switch - BUY TO CLOSE SUBMITTED')
                await asyncio.sleep(7)

            position, im_in_pos, pos_size, entry_px, pnl_perc, long = await self.get_position(market_index)

        logger.info('Position successfully closed in kill switch')

    async def pnl_close(self, market_index, entry_px):
        logger.info('Entering PNL close')
        position, im_in_pos, pos_size, _, pnl_perc, long = await self.get_position(market_index)

        if pnl_perc > self.take_profit:
            logger.info(f'PNL gain is {pnl_perc}% and target is {self.take_profit}%... closing position WIN')
            await self.kill_switch(market_index, market_index)
        elif pnl_perc <= self.max_loss:
            logger.info(f'PNL loss is {pnl_perc}% and max loss is {self.max_loss}%... closing position LOSS')
            await self.kill_switch(market_index, market_index)
        else:
            logger.info(f'PNL is {pnl_perc}% and within accepted range... not closing position')
        logger.info('Finished PNL close')

    async def bot(self):
        market_index, market_type = self.drift_client.get_market_index_and_type(self.market_name)
        funding_rate = await self.drift_client.get_funding_rate(market_index)

        position, im_in_pos, pos_size, entry_px, pnl_perc, long = await self.get_position(market_index)

        if not im_in_pos:
            if funding_rate < self.funding_rate_threshold:
                logger.info(f"Buy signal triggered. Funding rate: {funding_rate}")
                order_params = OrderParams(
                    order_type=OrderType.Market(),
                    market_type=market_type,
                    direction=PositionDirection.Long(),
                    market_index=market_index,
                    base_asset_amount=self.size,
                )
                await self.limit_order(order_params)
            elif funding_rate > self.short_funding_rate_threshold:
                logger.info(f"Short signal triggered. Funding rate: {funding_rate}")
                order_params = OrderParams(
                    order_type=OrderType.Market(),
                    market_type=market_type,
                    direction=PositionDirection.Short(),
                    base_asset_amount=self.size,
                    market_index=market_index
                )
                await self.limit_order(order_params)
        else:
            logger.info('In position.. checking PNL')
            await self.pnl_close(market_index, entry_px)

async def main():
    env = "mainnet"
    market_name = "SOL-PERP"

    funding_rate_threshold = -43
    short_funding_rate_threshold = 32
    take_profit = 0.05
    max_loss = 0.03
    size = 0.1

    keypath = os.environ.get("ANCHOR_WALLET")
    with open(os.path.expanduser(keypath), "r") as f:
        secret = json.load(f)

    kp = Keypair.from_bytes(bytes(secret))
    logger.info(f"Using public key: {kp.pubkey()}")

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

    strategy = FundingRateStrategy(drift_client, market_name, funding_rate_threshold, short_funding_rate_threshold, take_profit, max_loss, size)

    while True:
        try:
            await strategy.bot()
            await asyncio.sleep(60)  # Run the bot every minute
        except Exception as e:
            logger.error(f"Error in bot: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())

