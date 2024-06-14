'''
Drift Protocol connection and Supply Demand Zone Algo
'''
import os
import json
import time
import traceback
import ccxt
import pandas as pd
import datetime
import schedule
import requests

from anchorpy import Wallet
from solana.rpc import commitment
from driftpy.constants.config import configs
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

# Define global variables for trading parameters
symbol = 'SOL'
timeframe = '1h'  # for sdz zone
limit = 300  # for sdz
max_loss = -3
target = 12
size = 0.25

# Construct the trading symbol for Binance
binance_symbol = symbol + '/USD'
print(binance_symbol)


def get_ohlcv(binance_symbol, timeframe='1h', limit=100):
    """
    Fetches OHLCV data from the Coinbase exchange for the specified symbol and timeframe.
    
    :param binance_symbol: The trading symbol in the format 'BASE/QUOTE' (e.g., 'SOL/USD').
    :param timeframe: The timeframe for the OHLCV data (default: '1h').
    :param limit: The number of candles to fetch (default: 100).
    :return: A DataFrame containing the OHLCV data.
    """
    coinbase = ccxt.coinbase()
    
    ohlcv = coinbase.fetch_ohlcv(binance_symbol, timeframe, limit)

    print(ohlcv)
    
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    df = df.tail(limit)

    df['support'] = df[:-2]['close'].min()
    df['resis'] = df[:-2]['close'].max()  
    
    return df

def supply_demand_zones(timeframe, limit):
    '''
    Calculates supply and demand zones based on the specified timeframe and limit.
    
    :param timeframe: The timeframe for the OHLCV data.
    :param limit: The number of candles to consider.
    :return: A DataFrame containing the supply and demand zones.
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

async def limit_order(drift_client, order_params):
    """
    Places a limit order using the Drift client.
    
    :param drift_client: The DriftClient instance.
    :param order_params: The parameters for the limit order.
    :return: The order transaction signature.
    """
    order_tx_ix = None
    if order_params.direction == PositionDirection.Long():
        #order_ix = drift_client.place_perp_order_ix(order_params)
        order_tx_sig = await drift_client.place_perp_order(order_params)
    elif order_params.direction == PositionDirection.Short():
        #order_ix = drift_client.place_perp_order_ix(order_params)
        order_tx_sig = await drift_client.place_perp_order(order_params)

    #order_result = await drift_client.send_ixs(order_ix)

    if order_params.direction == PositionDirection.Long():
        print(f"limit BUY order placed, order tx: {order_tx_sig}")
    else:
        print(f"limit SELL order placed, order tx: {order_tx_sig}")

    return order_tx_sig

def get_position(drift_client, _market_index):
    """
    Retrieves the position information for the specified market index.
    
    :param drift_client: The DriftClient instance.
    :param _market_index: The market index.
    :return: A tuple containing the position information.
    """
    user = drift_client.get_user()

    in_pos = False
    size = 0
    entry_px = 0
    pnl_perc = 0
    is_long = None

    position = user.get_perp_position(_market_index)

    if position == None:
        print("No active positions")
        return position, in_pos, size, entry_px, pnl_perc, is_long
    else:  
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
    """
    Cancels all open orders using the Drift client.
    
    :param drift_client: The DriftClient instance.
    """
    user = drift_client.get_user()
    orders = await asyncio.to_thread(user.get_open_orders)
    print(orders)
    print('above are the open orders... need to cancel any...')
    for order in orders:
        print(f"cancelling order {order}")
        await drift_client.cancel_order(order.order_id)

async def kill_switch(drift_client, market_index, market_type):
    """
    Implements a kill switch to close the position when certain conditions are met.
    
    :param drift_client: The DriftClient instance.
    :param market_index: The market index.
    :param market_type: The market type.
    """
    oracle_price_data = drift_client.get_oracle_price_data_for_perp_market(market_index)
    position, im_in_pos, pos_size, entry_px, pnl_perc, long = get_position(drift_client, market_index)

    while im_in_pos:
        await cancel_all_orders(drift_client)

        market = drift_client.get_perp_market_account(market_index)
        bid = calculate_bid_price(market, oracle_price_data)
        ask = calculate_ask_price(market, oracle_price_data)

        pos_size = abs(pos_size)

        if long:
            order_params = OrderParams(
                order_type=OrderType.Limit(),
                market_type=market_type,
                direction=PositionDirection.Short(),
                market_index=market_index,
                base_asset_amount=int(pos_size * BASE_PRECISION),
                price=int(ask * PRICE_PRECISION),
                trigger_condition=OrderTriggerCondition.Above(),
                post_only=PostOnlyParams.TryPostOnly(),
            )
            await limit_order(drift_client, market_index, order_params)
            print('kill switch - SELL TO CLOSE SUBMITTED ')
            time.sleep(7)
        else:
            order_params = OrderParams(
                order_type=OrderType.Limit(),
                market_type=market_type,
                direction=PositionDirection.Long(),
                market_index=market_index,
                base_asset_amount=int(pos_size * BASE_PRECISION),
                price=int(bid * PRICE_PRECISION),
                trigger_condition=OrderTriggerCondition.Above(),
                post_only=PostOnlyParams.TryPostOnly(),
            )
            await limit_order(drift_client, market_index, order_params)
            print('kill switch - BUY TO CLOSE SUBMITTED ')
            time.sleep(7)
        
        position, im_in_pos, pos_size, entry_px, pnl_perc, long = get_position(drift_client, market_index)

    print('position successfully closed in kill switch')

async def pnl_close(drift_client, market_index):
    """
    Closes the position based on the PNL (Profit and Loss) target or maximum loss.
    
    :param drift_client: The DriftClient instance.
    :param market_index: The market index.
    """
    print('entering pnl close')
    position, im_in_pos, pos_size, entry_px, pnl_perc, long = get_position(drift_client, market_index)
    if pnl_perc > target:
        print(f'pnl gain is {pnl_perc} and target is {target}... closing position WIN')
        await kill_switch(drift_client, market_index)
    elif pnl_perc <= max_loss:
        print(f'pnl loss is {pnl_perc} and max loss is {max_loss}... closing position LOSS')
        await kill_switch(drift_client, market_index)
    else:
        print(f'pnl loss is {pnl_perc} and max loss is {max_loss} and target {target}... not closing position')
    print('finished with pnl close')

async def bot(drift_client, market_name):
    """
    Main bot function that implements the trading strategy.
    
    :param drift_client: The DriftClient instance.
    :param market_name: The market name (e.g., 'SOL-PERP').
    """
    sdz = supply_demand_zones(timeframe, limit)
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

    market_index, market_type = drift_client.get_market_index_and_type(market_name)
    print(f"market index: {market_index} and market type: {market_type}.")
    
    position, im_in_pos, pos_size, entry_px, pnl_perc, long = get_position(drift_client, market_index)
    
    print("position:", position)
    drift_user = drift_client.get_user()
    orders = drift_user.get_open_orders()
    open_order_prices = [order.price for order in orders]
    print(open_order_prices)

    if buy2 and sell2 in open_order_prices:
        new_orders_needed = False
        print('buy2 and sell2 in open orders')
    else:
        new_orders_needed = True
        print('no open orders')

    #if not im_in_pos and new_orders_needed:
    if new_orders_needed == True:
        print('not in position.. setting orders...')
        await cancel_all_orders(drift_client)
        print("Canceling orders")
        buy_order_params = OrderParams(
            order_type=OrderType.Limit(),
            market_type=market_type,
            direction=PositionDirection.Long(),
            market_index=market_index,
            base_asset_amount=int(size * BASE_PRECISION),
            price=int(buy2 * PRICE_PRECISION),
            trigger_condition=OrderTriggerCondition.Above(),
            post_only=PostOnlyParams.TryPostOnly(),
        )
        await limit_order(drift_client, buy_order_params)
        ("setting first limit order")

        sell_order_params = OrderParams(
            order_type=OrderType.Limit(),
            market_type=market_type,
            direction=PositionDirection.Short(),
            market_index=market_index,
            base_asset_amount=int(size * BASE_PRECISION),
            price=int(sell2 * PRICE_PRECISION),
            trigger_condition=OrderTriggerCondition.Above(),
            post_only=PostOnlyParams.TryPostOnly(),

        )
        await limit_order(drift_client, sell_order_params)
        ("setting second limit order")

    elif im_in_pos:
        print('we are in position.. checking PNL')
        await pnl_close(drift_client, market_index)
    else:
        print('orders already set... chilling')

async def main():
    """
    Main function to set up the Drift client and run the bot.
    """
    env = "devnet"
    market_name = "SOL-PERP"
    keypath = os.environ.get("ANCHOR_WALLET")
    spread = 0.01
    subaccount_id = 10

    # Load the secret key from the keypath file
    with open(os.path.expanduser(keypath), "r") as f:
        secret = json.load(f)
    kp = Keypair.from_bytes(bytes(secret))
    #kp = load_keypair(f)  
    print("using public key:", kp.pubkey())
    config = configs[env]
    wallet = Wallet(kp)

    # Check if the keypath is provided or set in the environment variable
    if keypath is None:
        if os.environ["ANCHOR_WALLET"] is None:
            raise NotImplementedError("need to provide keypath or set ANCHOR_WALLET")
        else:
            keypath = os.environ["ANCHOR_WALLET"]

    # Set the appropriate URL based on the environment (devnet or mainnet)
    if env == "devnet":
        url = "https://devnet.helius-rpc.com/?api-key=3a1ca16d-e181-4755-9fe7-eac27579b48c"
    elif env == "mainnet":
        url = "https://mainnet.helius-rpc.com/?api-key=3a1ca16d-e181-4755-9fe7-eac27579b48c"
    else:
        raise NotImplementedError("only devnet/mainnet env supported")

    connection = AsyncClient(url)
    market_index = -1

    # Find the market index for the specified market name in the perp markets
    for perp_market_config in config.perp_markets:
        if perp_market_config.symbol == market_name:
            market_index = perp_market_config.market_index

    # Find the market index for the specified market name in the spot markets
    for spot_market_config in config.spot_markets:
        if spot_market_config.symbol == market_name:
            market_index = spot_market_config.market_index

    #url = "https://solana-api.projectserum.com"
    #dev_net_url = "https://devnet.helius-rpc.com/?api-key=3a1ca16d-e181-4755-9fe7-eac27579b48c"
    #mainnet_url =  "https://mainnet.helius-rpc.com/?api-key=3a1ca16d-e181-4755-9fe7-eac27579b48c"
    
    # Check if a valid market index was found
    if market_index == -1:
        print("INVALID MARKET")
        return
    markets = [market_index]

    # Determine if the market is a perp or spot market
    is_perp = "PERP" in market_name.upper()
    market_type = MarketType.Perp() if is_perp else MarketType.Spot()

    # Create a DriftClient instance with the specified connection, wallet, environment, and account subscription
    drift_client = DriftClient(
        connection,
        wallet,
        str(env),
        account_subscription=AccountSubscriptionConfig("websocket"),
    )

    #await drift_client.initialize_user()
    
    # Add the user with the specified subaccount ID and subscribe to updates
    await drift_client.add_user(subaccount_id)
    await drift_client.subscribe()

    # Main loop to run the bot
    while True:
        try:
            # Run the bot with the specified drift client and market name
            await bot(drift_client, market_name)
            # Wait for 15 seconds before the next iteration
            await asyncio.sleep(15)
        except Exception as e:
            # Handle exceptions and print error details
            print('+++++ maybe an internet problem.. code failed. sleeping 10')
            print(e)
            traceback.print_exc()
            # Wait for 10 seconds before retrying
            await asyncio.sleep(10)

# Entry point of the script
if __name__ == "__main__":
    # Import asyncio and run the main function
    import asyncio
    asyncio.run(main())



# '''
# Drift Protocol connection and Supply Demand Zone Algo
# '''
# import os
# import json
# import time
# import traceback
# import ccxt
# import pandas as pd
# import datetime
# import schedule
# import requests

# from anchorpy import Wallet
# from solana.rpc import commitment
# from driftpy.constants.config import configs
# from solders.keypair import Keypair # type: ignore
# from solders.pubkey import Pubkey # type: ignore
# from solana.rpc.async_api import AsyncClient
# from driftpy.math.amm import calculate_bid_ask_price
# from driftpy.math.market import (calculate_bid_price, calculate_ask_price)
# #from driftpy.keypair import load_keypair

# from driftpy.account_subscription_config import AccountSubscriptionConfig
# from driftpy.constants.config import configs
# from driftpy.types import (
#     MarketType,
#     OrderType,
#     OrderParams,
#     PositionDirection,
#     OrderTriggerCondition,
#     PostOnlyParams,
# )
# from driftpy.drift_client import DriftClient
# from driftpy.constants.numeric_constants import BASE_PRECISION, PRICE_PRECISION
# from driftpy.math.spot_position import (
#     get_worst_case_token_amounts,
#     is_spot_position_available,
# )
# from driftpy.math.perp_position import (
#     calculate_position_pnl,
#     calculate_entry_price,
#     calculate_base_asset_value,
#     is_available
# )

# #to-do add leverage later
# symbol = 'SOL'
# timeframe = '1h'  # for sdz zone
# limit = 300  # for sdz
# max_loss = -3
# target = 12
# size = 0.25

# binance_symbol = symbol + '/USD'
# print(binance_symbol)


# def get_ohlcv(binance_symbol, timeframe='1h', limit=100):
#     coinbase = ccxt.coinbase()
    
#     ohlcv = coinbase.fetch_ohlcv(binance_symbol, timeframe, limit)

#     print(ohlcv)
    
#     df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#     df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

#     df = df.tail(limit)

#     df['support'] = df[:-2]['close'].min()
#     df['resis'] = df[:-2]['close'].max()  
    
#     return df

# def supply_demand_zones(timeframe, limit):
#     '''
#     We can now pass in a timeframe and limit to change supply/demand zone easily

#     outputs a data frame with supply and demand zones for each time frame
#     # this is supply zone and demand zone ranges
#     # row 0 is the CLOSE, row 1 is the WICK (high/low)
#     # and the supply/demand zone is in between the two
#     '''

#     print('starting supply and demand zone calculations..')

#     # get OHLCV data     
#     sd_df = pd.DataFrame() # supply and demand zone dataframe 

#     df = get_ohlcv(binance_symbol, timeframe, limit)
#     print(df)
    
#     supp_1h = df.iloc[-1]['support']
#     resis_1h = df.iloc[-1]['resis']

#     df['supp_lo'] = df[:-2]['low'].min()
#     supp_lo_1h = df.iloc[-1]['supp_lo']

#     df['res_hi'] = df[:-2]['high'].max()
#     res_hi_1h = df.iloc[-1]['res_hi']

#     sd_df['1h_dz'] = [supp_lo_1h, supp_1h]
#     sd_df['1h_sz'] = [res_hi_1h, resis_1h]

#     return sd_df # this is a df where the zone is indicated per timeframe
#                 # and range is between row 0 and 1

# async def limit_order(drift_client, order_params):
#     order_tx_ix = None
#     if order_params.direction == PositionDirection.Long():
#         #order_ix = drift_client.place_perp_order_ix(order_params)
#         order_tx_sig = await drift_client.place_perp_order(order_params)
#     elif order_params.direction == PositionDirection.Short():
#         #order_ix = drift_client.place_perp_order_ix(order_params)
#         order_tx_sig = await drift_client.place_perp_order(order_params)

#     #order_result = await drift_client.send_ixs(order_ix)

#     if order_params.direction == PositionDirection.Long():
#         print(f"limit BUY order placed, order tx: {order_tx_sig}")
#     else:
#         print(f"limit SELL order placed, order tx: {order_tx_sig}")

#     return order_tx_sig

# def get_position(drift_client, _market_index):
#     user = drift_client.get_user()

#     in_pos = False
#     size = 0
#     entry_px = 0
#     pnl_perc = 0
#     is_long = None

#     position = user.get_perp_position(_market_index)

#     if position == None:
#         print("No active positions")
#         return position, in_pos, size, entry_px, pnl_perc, is_long
#     else:  
#         entry_px = calculate_entry_price(position)
#         in_pos = True if position != None else False
#         market = drift_client.get_perp_market_account(_market_index)
#         #pnl_perc = calculate_position_pnl(market, position, oracle_price_data)
#         pnl_perc = user.get_unrealized_pnl(_market_index)
#         base_asset_amount = position.base_asset_amount if position is not None else 0

#         is_long = base_asset_amount > 0
#         size = base_asset_amount
#         #is_short = base_asset_amount < 0

#         return position, in_pos, size, entry_px, pnl_perc, is_long

# async def cancel_all_orders(drift_client):
#     user = drift_client.get_user()
#     orders = await asyncio.to_thread(user.get_open_orders)
#     print(orders)
#     print('above are the open orders... need to cancel any...')
#     for order in orders:
#         print(f"cancelling order {order}")
#         await drift_client.cancel_order(order.order_id)

# async def kill_switch(drift_client, market_index, market_type):
#     oracle_price_data = drift_client.get_oracle_price_data_for_perp_market(market_index)
#     position, im_in_pos, pos_size, entry_px, pnl_perc, long = get_position(drift_client, market_index)

#     while im_in_pos:
#         await cancel_all_orders(drift_client)

#         market = drift_client.get_perp_market_account(market_index)
#         bid = calculate_bid_price(market, oracle_price_data)
#         ask = calculate_ask_price(market, oracle_price_data)

#         pos_size = abs(pos_size)

#         if long:
#             order_params = OrderParams(
#                 order_type=OrderType.Limit(),
#                 market_type=market_type,
#                 direction=PositionDirection.Short(),
#                 market_index=market_index,
#                 base_asset_amount=int(pos_size * BASE_PRECISION),
#                 price=int(ask * PRICE_PRECISION),
#                 trigger_condition=OrderTriggerCondition.Above(),
#                 post_only=PostOnlyParams.TryPostOnly(),
#             )
#             await limit_order(drift_client, market_index, order_params)
#             print('kill switch - SELL TO CLOSE SUBMITTED ')
#             time.sleep(7)
#         else:
#             order_params = OrderParams(
#                 order_type=OrderType.Limit(),
#                 market_type=market_type,
#                 direction=PositionDirection.Long(),
#                 market_index=market_index,
#                 base_asset_amount=int(pos_size * BASE_PRECISION),
#                 price=int(bid * PRICE_PRECISION),
#                 trigger_condition=OrderTriggerCondition.Above(),
#                 post_only=PostOnlyParams.TryPostOnly(),
#             )
#             await limit_order(drift_client, market_index, order_params)
#             print('kill switch - BUY TO CLOSE SUBMITTED ')
#             time.sleep(7)
        
#         position, im_in_pos, pos_size, entry_px, pnl_perc, long = get_position(drift_client, market_index)

#     print('position successfully closed in kill switch')

# async def pnl_close(drift_client, market_index):
#     print('entering pnl close')
#     position, im_in_pos, pos_size, entry_px, pnl_perc, long = get_position(drift_client, market_index)
#     if pnl_perc > target:
#         print(f'pnl gain is {pnl_perc} and target is {target}... closing position WIN')
#         await kill_switch(drift_client, market_index)
#     elif pnl_perc <= max_loss:
#         print(f'pnl loss is {pnl_perc} and max loss is {max_loss}... closing position LOSS')
#         await kill_switch(drift_client, market_index)
#     else:
#         print(f'pnl loss is {pnl_perc} and max loss is {max_loss} and target {target}... not closing position')
#     print('finished with pnl close')

# async def bot(drift_client, market_name):
    
#     sdz = supply_demand_zones(timeframe, limit)
#     print(sdz)

#     sz_1hr = sdz['1h_sz']
#     sz_1hr_0 = sz_1hr.iloc[0]
#     sz_1hr_1 = sz_1hr.iloc[-1]

#     dz_1hr = sdz['1h_dz']
#     dz_1hr_0 = dz_1hr.iloc[0]
#     dz_1hr_1 = dz_1hr.iloc[-1]

#     buy1 = max(dz_1hr_0, dz_1hr_1)
#     buy2 = (dz_1hr_0 + dz_1hr_1) / 2

#     sell1 = min(sz_1hr_0, sz_1hr_1)
#     sell2 = (sz_1hr_0 + sz_1hr_1) / 2

#     market_index, market_type = drift_client.get_market_index_and_type(market_name)
#     print(f"market index: {market_index} and market type: {market_type}.")
    
#     position, im_in_pos, pos_size, entry_px, pnl_perc, long = get_position(drift_client, market_index)
    
#     print("position:", position)
#     drift_user = drift_client.get_user()
#     orders = drift_user.get_open_orders()
#     open_order_prices = [order.price for order in orders]
#     print(open_order_prices)

#     if buy2 and sell2 in open_order_prices:
#         new_orders_needed = False
#         print('buy2 and sell2 in open orders')
#     else:
#         new_orders_needed = True
#         print('no open orders')

#     #if not im_in_pos and new_orders_needed:
#     if new_orders_needed == True:
#         print('not in position.. setting orders...')
#         await cancel_all_orders(drift_client)
#         print("Canceling orders")
#         buy_order_params = OrderParams(
#             order_type=OrderType.Limit(),
#             market_type=market_type,
#             direction=PositionDirection.Long(),
#             market_index=market_index,
#             base_asset_amount=int(size * BASE_PRECISION),
#             price=int(buy2 * PRICE_PRECISION),
#             trigger_condition=OrderTriggerCondition.Above(),
#             post_only=PostOnlyParams.TryPostOnly(),
#         )
#         await limit_order(drift_client, buy_order_params)
#         ("setting first limit order")

#         sell_order_params = OrderParams(
#             order_type=OrderType.Limit(),
#             market_type=market_type,
#             direction=PositionDirection.Short(),
#             market_index=market_index,
#             base_asset_amount=int(size * BASE_PRECISION),
#             price=int(sell2 * PRICE_PRECISION),
#             trigger_condition=OrderTriggerCondition.Above(),
#             post_only=PostOnlyParams.TryPostOnly(),

#         )
#         await limit_order(drift_client, sell_order_params)
#         ("setting second limit order")

#     elif im_in_pos:
#         print('we are in position.. checking PNL')
#         await pnl_close(drift_client, market_index)
#     else:
#         print('orders already set... chilling')

# async def main(
# ):
#     env = "devnet"
#     market_name = "SOL-PERP"
#     keypath = os.environ.get("ANCHOR_WALLET")
#     spread=0.01
#     subaccount_id = 10

#     with open(os.path.expanduser(keypath), "r") as f:
#         secret = json.load(f)
#     kp = Keypair.from_bytes(bytes(secret))
#     #kp = load_keypair(f)  
#     print("using public key:", kp.pubkey())
#     config = configs[env]
#     wallet = Wallet(kp)

#     if keypath is None:
#         if os.environ["ANCHOR_WALLET"] is None:
#             raise NotImplementedError("need to provide keypath or set ANCHOR_WALLET")
#         else:
#             keypath = os.environ["ANCHOR_WALLET"]

#     if env == "devnet":
#         url = "https://devnet.helius-rpc.com/?api-key=3a1ca16d-e181-4755-9fe7-eac27579b48c"
#     elif env == "mainnet":
#         url = "https://mainnet.helius-rpc.com/?api-key=3a1ca16d-e181-4755-9fe7-eac27579b48c"
#     else:
#         raise NotImplementedError("only devnet/mainnet env supported")

#     connection = AsyncClient(url)
#     market_index = -1
#     for perp_market_config in config.perp_markets:
#         if perp_market_config.symbol == market_name:
#             market_index = perp_market_config.market_index
#     for spot_market_config in config.spot_markets:
#         if spot_market_config.symbol == market_name:
#             market_index = spot_market_config.market_index

#     #url = "https://solana-api.projectserum.com"
#     #dev_net_url = "https://devnet.helius-rpc.com/?api-key=3a1ca16d-e181-4755-9fe7-eac27579b48c"
#     #mainnet_url =  "https://mainnet.helius-rpc.com/?api-key=3a1ca16d-e181-4755-9fe7-eac27579b48c"
    
#     if market_index == -1:
#         print("INVALID MARKET")
#         return
#     markets = [market_index]

#     is_perp = "PERP" in market_name.upper()
#     market_type = MarketType.Perp() if is_perp else MarketType.Spot()

#     drift_client = DriftClient(
#         connection,
#         wallet,
#         str(env),
#         account_subscription=AccountSubscriptionConfig("websocket"),
#     )

#     #await drift_client.initialize_user()
    
#     await drift_client.add_user(subaccount_id)
#     await drift_client.subscribe()

#     while True:
#         try:
#             await bot(drift_client, market_name)
#             await asyncio.sleep(15)
#         except Exception as e:
#             print('+++++ maybe an internet problem.. code failed. sleeping 10')
#             print(e)
#             traceback.print_exc()
#             await asyncio.sleep(10)

# if __name__ == "__main__":

#     import asyncio
#     asyncio.run(main())


    