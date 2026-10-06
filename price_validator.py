import MetaTrader5 as mt5
from trade_request import TradeRequest

# Maximum allowed distance from signal entry
MAX_DISTANCE = 1.00   # $1.00 for XAUUSD


def is_entry_valid(trade: TradeRequest):

    tick = mt5.symbol_info_tick(trade.symbol)

    if tick is None:
        print("Could not get market price.")
        return False

    if trade.direction == "BUY":
        current_price = tick.ask
    else:
        current_price = tick.bid

    distance = abs(current_price - trade.entry)

    print("\n========== ENTRY CHECK ==========")
    print(f"Signal Entry: {trade.entry}")
    print(f"Current Price: {current_price}")
    print(f"Distance: {distance:.2f}")
    print(f"Maximum Allowed: {MAX_DISTANCE}")
    print("=================================")

    if distance > MAX_DISTANCE:
        print("Signal rejected: market moved too far.")
        return False

    print("Signal accepted.")
    return True