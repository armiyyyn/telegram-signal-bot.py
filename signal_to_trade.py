from signal_parser import parse_signal, ParsedSignal
from trade_request import TradeRequest


def convert_signal_to_trade(signal: ParsedSignal, current_price: float) -> TradeRequest | None:
    """
    Convert a parsed XNINE signal into a TradeRequest.

    The actual entry is the current MT5 market price.
    The Telegram entry zone is used to validate whether
    the signal is still actionable.
    """

    if signal.symbol != "XAUUSD":
        print("ERROR: Only XAUUSD signals are supported.")
        return None

    if signal.direction not in ("BUY", "SELL"):
        print("ERROR: Invalid trade direction.")
        return None

    if not signal.take_profits:
        print("ERROR: Signal contains no take profits.")
        return None

    # Check whether the current market price is inside
    # the Telegram entry zone.
    if not (
        signal.entry_low <= current_price <= signal.entry_high
    ):
        print(
            f"Signal rejected: current price {current_price:.2f} "
            f"is outside entry zone "
            f"{signal.entry_low:.2f} - {signal.entry_high:.2f}."
        )
        return None

    trade = TradeRequest(
        symbol=signal.symbol,
        direction=signal.direction,
        volume=0.01,
        entry=current_price,
        stop_loss=signal.stop_loss,
        take_profit=signal.take_profits[0],
    )

    return trade


if __name__ == "__main__":

    test_signal = """
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

    signal = parse_signal(test_signal)

    if signal is None:
        print("Signal parsing failed.")
    else:

        trade = convert_signal_to_trade(signal)

        if trade is None:
            print("Signal conversion failed.")
        else:

            print("\n========== TRADE REQUEST ==========")
            print(f"Symbol:     {trade.symbol}")
            print(f"Direction:  {trade.direction}")
            print(f"Volume:     {trade.volume}")
            print(f"Entry:      {trade.entry:.2f}")
            print(f"SL:         {trade.stop_loss}")
            print(f"TP1:        {trade.take_profit}")
            print("===================================")