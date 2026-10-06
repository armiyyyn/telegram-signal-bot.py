import MetaTrader5 as mt5


def connect_to_mt5():
    if not mt5.initialize():
        print(f"MT5 initialization failed: {mt5.last_error()}")
        return False

    print("Connected to MetaTrader 5.")
    return True


def show_account_information():
    account = mt5.account_info()

    if account is None:
        print(f"Could not read account information: {mt5.last_error()}")
        return

    print("\n========== ACCOUNT INFORMATION ==========")
    print(f"Login: {account.login}")
    print(f"Server: {account.server}")
    print(f"Currency: {account.currency}")
    print(f"Balance: {account.balance}")
    print(f"Equity: {account.equity}")
    print(f"Leverage: 1:{account.leverage}")
    print("=========================================\n")


def main():
    if not connect_to_mt5():
        return

    try:
        show_account_information()
    finally:
        mt5.shutdown()
        print("Disconnected from MetaTrader 5.")


if __name__ == "__main__":
    main()