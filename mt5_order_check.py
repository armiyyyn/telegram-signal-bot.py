import MetaTrader5 as mt5

from trade_request import TradeRequest, validate_trade_request


SYMBOL = "XAUUSD"


def connect_to_mt5():
    if not mt5.initialize():
        print(f"MT5 initialization failed: {mt5.last_error()}")
        return False

    print("Connected to MetaTrader 5.")
    return True


def prepare_order(trade: TradeRequest):
    """
    Prepare an MT5 market order request.
    This function does NOT send the order.
    """

    tick = mt5.symbol_info_tick(trade.symbol)

    if tick is None:
        print(f"Could not get current price for {trade.symbol}.")
        return None

    if trade.direction == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        market_price = tick.ask
    else:
        order_type = mt5.ORDER_TYPE_SELL
        market_price = tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": trade.symbol,
        "volume": trade.volume,
        "type": order_type,
        "price": market_price,
        "sl": trade.stop_loss,
        "tp": trade.take_profit,
        "deviation": 20,
        "magic": 100001,
        "comment": "Telegram XAU algo",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    return request


def check_order(request):
    """
    Ask MT5 whether the order request is valid.
    This does NOT place the order.
    """

    result = mt5.order_check(request)

    if result is None:
        print(f"Order check failed: {mt5.last_error()}")
        return False

    print("\n========== MT5 ORDER CHECK ==========")
    print(f"Retcode: {result.retcode}")
    print(f"Comment: {result.comment}")
    print(f"Balance: {result.balance}")
    print(f"Equity: {result.equity}")
    print(f"Margin: {result.margin}")
    print(f"Margin free: {result.margin_free}")
    print("=====================================")

    return True


def main():

    test_trade = TradeRequest(
        symbol=SYMBOL,
        direction="BUY",
        volume=0.01,
        entry=4359.00,
        stop_loss=4354.00,
        take_profit=4364.00,
    )

    print("\n========== TRADE REQUEST ==========")
    print(f"Symbol:     {test_trade.symbol}")
    print(f"Direction:  {test_trade.direction}")
    print(f"Volume:     {test_trade.volume}")
    print(f"Entry:      {test_trade.entry}")
    print(f"SL:         {test_trade.stop_loss}")
    print(f"TP1:        {test_trade.take_profit}")
    print("===================================")

    if not validate_trade_request(test_trade):
        return

    if not connect_to_mt5():
        return

    try:
        request = prepare_order(test_trade)

        if request is None:
            return

        print("\n========== PREPARED MT5 ORDER ==========")
        print(f"Symbol:     {request['symbol']}")
        print(f"Type:       {'BUY' if test_trade.direction == 'BUY' else 'SELL'}")
        print(f"Volume:     {request['volume']}")
        print(f"Market:     {request['price']}")
        print(f"SL:         {request['sl']}")
        print(f"TP:         {request['tp']}")
        print("========================================")

        check_order(request)

    finally:
        mt5.shutdown()
        print("\nDisconnected from MetaTrader 5.")


if __name__ == "__main__":
    main()