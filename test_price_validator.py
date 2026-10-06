import MetaTrader5 as mt5

from trade_request import TradeRequest
from price_validator import is_entry_valid


if not mt5.initialize():
    print("MT5 connection failed.")
    quit()

trade = TradeRequest(
    symbol="XAUUSD",
    direction="BUY",
    volume=0.01,
    entry=4363.98,      # adjust close to market
    stop_loss=4359.00,
    take_profit=4369.00
)

is_entry_valid(trade)

mt5.shutdown()