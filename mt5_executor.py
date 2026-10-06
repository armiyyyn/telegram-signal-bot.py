import MetaTrader5 as mt5

from signal_parser import ParsedSignal, parse_signal
from trade_request import TradeRequest, validate_trade_request


MAX_DISTANCE = 1.00
MAGIC_NUMBER = 100001


def connect_to_mt5():
    if not mt5.initialize():
        print(f"MT5 initialization failed: {mt5.last_error()}")
        return False

    print("Connected to MetaTrader 5.")
    return True


def get_market_price(signal: ParsedSignal):
    """
    Get the correct executable market price.

    BUY  -> Ask
    SELL -> Bid
    """

    tick = mt5.symbol_info_tick(signal.symbol)

    if tick is None:
        print(f"Could not get current price for {signal.symbol}.")
        return None

    if signal.direction == "BUY":
        return tick.ask

    return tick.bid


def validate_entry_zone(signal: ParsedSignal, market_price: float):
    """
    Validate the current market price against the signal entry zone.

    The signal zone is the primary validation.
    MAX_DISTANCE is an additional safety limit.
    """

    print("\n========== ENTRY VALIDATION ==========")
    print(f"Direction:    {signal.direction}")
    print(f"Entry low:    {signal.entry_low:.2f}")
    print(f"Entry high:   {signal.entry_high:.2f}")
    print(f"Market price: {market_price:.2f}")

    # --------------------------------------------------
    # Check whether price is inside the signal zone
    # --------------------------------------------------

    if signal.entry_low <= market_price <= signal.entry_high:
        print("Price is inside the signal entry zone.")
    else:
        distance_to_zone = min(
            abs(market_price - signal.entry_low),
            abs(market_price - signal.entry_high),
        )

        print(
            f"Price is outside the entry zone "
            f"by {distance_to_zone:.2f}."
        )

        if distance_to_zone > MAX_DISTANCE:
            print("Signal rejected: market moved too far.")
            print("=====================================")
            return False

        print(
            f"Price is outside the zone, but within the "
            f"{MAX_DISTANCE:.2f} safety distance."
        )

    print("Entry validation passed.")
    print("=====================================")

    return True


def create_trade_request(signal: ParsedSignal, market_price: float):
    """
    Convert a parsed Telegram signal into a TradeRequest.

    Uses:
    - 0.01 lot
    - current market price
    - TP1 only
    - signal SL
    """

    trade = TradeRequest(
        symbol=signal.symbol,
        direction=signal.direction,
        volume=0.01,
        entry=market_price,
        stop_loss=signal.stop_loss,
        take_profit=signal.take_profits[0],
    )

    return trade


def prepare_order(trade: TradeRequest):
    """
    Prepare a market order.
    Does NOT send the order.
    """

    tick = mt5.symbol_info_tick(trade.symbol)

    if tick is None:
        print(f"Could not get current price for {trade.symbol}.")
        return None

    if trade.direction == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        market_price = tick.ask

        if trade.take_profit <= market_price:
            print("ERROR: BUY TP is no longer above market price.")
            return None

        if trade.stop_loss >= market_price:
            print("ERROR: BUY SL is no longer below market price.")
            return None

    else:
        order_type = mt5.ORDER_TYPE_SELL
        market_price = tick.bid

        if trade.take_profit >= market_price:
            print("ERROR: SELL TP is no longer below market price.")
            return None

        if trade.stop_loss <= market_price:
            print("ERROR: SELL SL is no longer above market price.")
            return None

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": trade.symbol,
        "volume": trade.volume,
        "type": order_type,
        "price": market_price,
        "sl": trade.stop_loss,
        "tp": trade.take_profit,
        "deviation": 20,
        "magic": MAGIC_NUMBER,
        "comment": "Telegram XAU algo",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    return request


def check_order(request):
    """
    Check whether MT5 accepts the order.
    Does NOT send the order.
    """

    result = mt5.order_check(request)

    if result is None:
        print(f"Order check failed: {mt5.last_error()}")
        return False

    print("\n========== MT5 ORDER CHECK ==========")
    print(f"Retcode:      {result.retcode}")
    print(f"Comment:      {result.comment}")
    print(f"Balance:      {result.balance}")
    print(f"Equity:       {result.equity}")
    print(f"Margin:       {result.margin}")
    print(f"Margin free:  {result.margin_free}")
    print("=====================================")

    return result.retcode == 0


def execute_order(request):
    """
    Send the order to MT5.
    """

    print("\n========== SENDING ORDER ==========")

    result = mt5.order_send(request)

    if result is None:
        print(f"Order send failed: {mt5.last_error()}")
        return False

    print(f"Retcode: {result.retcode}")
    print(f"Comment: {result.comment}")

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("ORDER WAS NOT EXECUTED.")
        return False

    print("ORDER EXECUTED SUCCESSFULLY.")
    print(f"Order ticket: {result.order}")
    print(f"Deal ticket: {result.deal}")
    print("===================================")

    return True


if __name__ == "__main__":

    # --------------------------------------------------
    # REAL XNINE SIGNAL TEST
    # --------------------------------------------------

    test_signal_text = """
    Algorithm is selling XAUUSD

    📍4155.09 - 4162.78

    ✅ TP 1: 4151.24

    ✅ TP 2: 4147.4

    ✅ TP 3: 4139.71

    ✅ TP 4: 4124.32

    ✅ TP 5: 4093.55

    ❗️ SL: 4178.17

    #algoxnine
    """

    print("\n==========================================")
    print("TELEGRAM → MT5 DEMO EXECUTION TEST")
    print("==========================================")

    # --------------------------------------------------
    # 1. Parse Telegram signal
    # --------------------------------------------------

    signal = parse_signal(test_signal_text)

    if signal is None:
        print("Signal parsing failed.")
        raise SystemExit

    print("\n========== PARSED SIGNAL ==========")
    print(f"Symbol:      {signal.symbol}")
    print(f"Direction:   {signal.direction}")
    print(f"Entry zone:  {signal.entry_low:.2f} - {signal.entry_high:.2f}")
    print(f"TP1:         {signal.take_profits[0]:.2f}")
    print(f"SL:          {signal.stop_loss:.2f}")
    print("===================================")

    # --------------------------------------------------
    # 2. Connect to MT5
    # --------------------------------------------------

    if not connect_to_mt5():
        raise SystemExit

    try:

        # --------------------------------------------------
        # 3. Get live executable price
        # --------------------------------------------------

        market_price = get_market_price(signal)

        if market_price is None:
            raise SystemExit

        print("\n========== LIVE MARKET PRICE ==========")
        print(f"{signal.symbol}: {market_price:.2f}")
        print("=======================================")

        # --------------------------------------------------
        # 4. Validate entry zone
        # --------------------------------------------------

        if not validate_entry_zone(signal, market_price):
            print("Trade rejected during entry validation.")
            raise SystemExit

        # --------------------------------------------------
        # 5. Create TradeRequest
        # --------------------------------------------------

        trade = create_trade_request(signal, market_price)

        print("\n========== TRADE REQUEST ==========")
        print(f"Symbol:     {trade.symbol}")
        print(f"Direction:  {trade.direction}")
        print(f"Volume:     {trade.volume}")
        print(f"Entry:      {trade.entry:.2f}")
        print(f"SL:         {trade.stop_loss:.2f}")
        print(f"TP1:        {trade.take_profit:.2f}")
        print("===================================")

        # --------------------------------------------------
        # 6. Validate trade structure
        # --------------------------------------------------

        if not validate_trade_request(trade):
            print("Trade rejected during trade validation.")
            raise SystemExit

        # --------------------------------------------------
        # 7. Prepare MT5 order
        # --------------------------------------------------

        request = prepare_order(trade)

        if request is None:
            print("Trade rejected during order preparation.")
            raise SystemExit

        print("\n========== PREPARED MT5 ORDER ==========")
        print(
            f"Type:         "
            f"{'BUY' if trade.direction == 'BUY' else 'SELL'}"
        )
        print(f"Symbol:       {request['symbol']}")
        print(f"Volume:       {request['volume']}")
        print(f"Market price: {request['price']:.2f}")
        print(f"SL:           {request['sl']:.2f}")
        print(f"TP:           {request['tp']:.2f}")
        print("========================================")

        # --------------------------------------------------
        # 8. MT5 order check
        # --------------------------------------------------

        if not check_order(request):
            print("Trade rejected by MT5 order check.")
            raise SystemExit

        # --------------------------------------------------
        # 9. Manual safety confirmation
        # --------------------------------------------------

        print("\n==========================================")
        print("READY TO SEND DEMO ORDER")
        print("==========================================")

        confirmation = input(
            "Type YES to send the 0.01 demo order: "
        )

        if confirmation != "YES":
            print("Order cancelled by user.")
            raise SystemExit

        # --------------------------------------------------
        # 10. Execute
        # --------------------------------------------------

        execute_order(request)

    finally:
        mt5.shutdown()
        print("\nDisconnected from MetaTrader 5.")