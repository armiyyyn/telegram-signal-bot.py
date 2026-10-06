from dataclasses import dataclass


@dataclass
class TradeRequest:
    symbol: str
    direction: str
    volume: float
    entry: float
    stop_loss: float
    take_profit: float


def validate_trade_request(trade: TradeRequest) -> bool:
    """
    Validate the basic structure and price relationships
    of a trade request.
    """

    if trade.symbol != "XAUUSD":
        print("ERROR: Invalid symbol.")
        return False

    if trade.direction not in ("BUY", "SELL"):
        print("ERROR: Direction must be BUY or SELL.")
        return False

    if trade.volume != 0.01:
        print("ERROR: First version only allows 0.01 lots.")
        return False

    if trade.entry <= 0:
        print("ERROR: Entry price must be positive.")
        return False

    if trade.stop_loss <= 0:
        print("ERROR: Stop loss must be positive.")
        return False

    if trade.take_profit <= 0:
        print("ERROR: Take profit must be positive.")
        return False

    if trade.direction == "BUY":
        if trade.stop_loss >= trade.entry:
            print("ERROR: BUY stop loss must be below entry.")
            return False

        if trade.take_profit <= trade.entry:
            print("ERROR: BUY take profit must be above entry.")
            return False

    if trade.direction == "SELL":
        if trade.stop_loss <= trade.entry:
            print("ERROR: SELL stop loss must be above entry.")
            return False

        if trade.take_profit >= trade.entry:
            print("ERROR: SELL take profit must be below entry.")
            return False

    print("Trade request is valid.")
    return True


if __name__ == "__main__":

    test_trade = TradeRequest(
        symbol="XAUUSD",
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

    validate_trade_request(test_trade)