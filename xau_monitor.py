import time
import MetaTrader5 as mt5


SYMBOL = "XAUUSD"


def main():
    if not mt5.initialize():
        print(f"MT5 initialization failed: {mt5.last_error()}")
        return

    print("Connected to MetaTrader 5.")
    print(f"Monitoring {SYMBOL}...")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            tick = mt5.symbol_info_tick(SYMBOL)

            if tick is None:
                print(f"Could not get {SYMBOL} price.")
                time.sleep(1)
                continue

            bid = tick.bid
            ask = tick.ask
            spread = ask - bid

            print(
                f"\r{SYMBOL} | "
                f"Bid: {bid:.2f} | "
                f"Ask: {ask:.2f} | "
                f"Spread: {spread:.2f}",
                end="",
                flush=True
            )

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nMonitor stopped by user.")

    finally:
        mt5.shutdown()
        print("Disconnected from MetaTrader 5.")


if __name__ == "__main__":
    main()