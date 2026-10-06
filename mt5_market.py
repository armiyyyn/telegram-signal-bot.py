import MetaTrader5 as mt5


SYMBOL = "XAUUSD"


def connect_to_mt5():
    if not mt5.initialize():
        print(f"MT5 initialization failed: {mt5.last_error()}")
        return False

    print("Connected to MetaTrader 5.")
    return True


def check_symbol():
    symbol_info = mt5.symbol_info(SYMBOL)

    if symbol_info is None:
        print(f"\nSymbol {SYMBOL} was not found.")
        print(f"MT5 error: {mt5.last_error()}")
        return False

    print("\n========== SYMBOL INFORMATION ==========")
    print(f"Symbol: {symbol_info.name}")
    print(f"Visible: {symbol_info.visible}")
    print(f"Trade mode: {symbol_info.trade_mode}")
    print(f"Minimum volume: {symbol_info.volume_min}")
    print(f"Maximum volume: {symbol_info.volume_max}")
    print(f"Volume step: {symbol_info.volume_step}")
    print(f"Digits: {symbol_info.digits}")
    print(f"Point: {symbol_info.point}")
    print(f"Tick size: {symbol_info.trade_tick_size}")
    print(f"Tick value: {symbol_info.trade_tick_value}")
    print("=========================================")

    return True


def show_current_price():
    tick = mt5.symbol_info_tick(SYMBOL)

    if tick is None:
        print(f"\nCould not get price for {SYMBOL}.")
        print(f"MT5 error: {mt5.last_error()}")
        return

    print("\n========== CURRENT PRICE ==========")
    print(f"Bid: {tick.bid}")
    print(f"Ask: {tick.ask}")
    print(f"Last: {tick.last}")
    print("===================================")


def main():
    if not connect_to_mt5():
        return

    try:
        if not check_symbol():
            return

        show_current_price()

    finally:
        mt5.shutdown()
        print("\nDisconnected from MetaTrader 5.")


if __name__ == "__main__":
    main()