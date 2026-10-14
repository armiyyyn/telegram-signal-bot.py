import os

from dotenv import load_dotenv
from telethon import TelegramClient, events

from signal_parser import parse_signal
from mt5_executor import (
    connect_to_mt5,
    get_market_price,
    validate_entry_zone,
    create_trade_request,
)

#Hello test
# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")

XAU_ALGO_1M_TOPIC_ID = 114

# Put your actual XNINE LEVEL 1 chat ID here.
SIGNAL_CHANNELS = [
    -1003854878353
]


# --------------------------------------------------
# Telegram client
# --------------------------------------------------

client = TelegramClient(
    "telegram_windows_session",
    API_ID,
    API_HASH,
)


# --------------------------------------------------
# MT5 connection
# --------------------------------------------------

mt5_connected = connect_to_mt5()

if not mt5_connected:
    print("Could not connect to MT5.")
    raise SystemExit


# --------------------------------------------------
# Telegram message handler
# --------------------------------------------------

@client.on(events.NewMessage)
async def new_message(event):
    # Only listen to the XNINE LEVEL 1 group.
    if event.chat_id not in SIGNAL_CHANNELS:
        return

    reply_to = event.message.reply_to

    # Identify the topic for both setup messages and replies.
    if reply_to:
        topic_id = (
            reply_to.reply_to_top_id
            if reply_to.reply_to_top_id is not None
            else reply_to.reply_to_msg_id
        )
    else:
        topic_id = event.message.id

    # Ignore every topic except XAU Algo 1M (Topic 114).
    if topic_id != XAU_ALGO_1M_TOPIC_ID:
        return

    # Get and print every message in Topic 114.
    text = event.raw_text

    if not text or not text.strip():
        return

    print("\n\n==========================================")
    print("NEW XAU ALGO 1M TELEGRAM MESSAGE")
    print("==========================================")
    print(text)
    print("==========================================")

    # ----------------------------------------------
    # 4. Parse signal
    # ----------------------------------------------

    signal = parse_signal(text)

    if signal is None:
        print("Signal parsing failed.")
        return

    print("\n========== PARSED SIGNAL ==========")
    print(f"Symbol:      {signal.symbol}")
    print(f"Direction:   {signal.direction}")
    print(
        f"Entry zone:  "
        f"{signal.entry_low:.2f} - {signal.entry_high:.2f}"
    )
    print(f"TP1:         {signal.take_profits[0]:.2f}")
    print(f"SL:          {signal.stop_loss:.2f}")
    print("===================================")

    # ----------------------------------------------
    # 5. Get live MT5 price
    # ----------------------------------------------

    market_price = get_market_price(signal)

    if market_price is None:
        print("Could not get current MT5 price.")
        return

    print("\n========== LIVE MARKET PRICE ==========")
    print(f"{signal.symbol}: {market_price:.2f}")
    print("=======================================")

    # ----------------------------------------------
    # 6. Validate entry
    # ----------------------------------------------

    if not validate_entry_zone(signal, market_price):
        print("SIGNAL REJECTED.")
        return

    # ----------------------------------------------
    # 7. Create trade request
    # ----------------------------------------------

    trade = create_trade_request(signal, market_price)

    print("\n========== TRADE THAT WOULD BE SENT ==========")
    print(f"Symbol:     {trade.symbol}")
    print(f"Direction:  {trade.direction}")
    print(f"Volume:     {trade.volume}")
    print(f"Entry:      {trade.entry:.2f}")
    print(f"SL:         {trade.stop_loss:.2f}")
    print(f"TP1:        {trade.take_profit:.2f}")
    print("==============================================")

    # ----------------------------------------------
    # 8. IMPORTANT:
    #    DO NOT SEND ORDER YET
    # ----------------------------------------------

    print("\n*** DRY RUN ONLY ***")
    print("No MT5 order was sent.")


# --------------------------------------------------
# Start
# --------------------------------------------------

print("\n==========================================")
print("WINDOWS TELEGRAM → MT5 DRY RUN")
print("==========================================")
print("MT5 connected.")
print(f"Listening for Topic ID: {XAU_ALGO_1M_TOPIC_ID}")
print("Waiting for XAU algo 1M signals...")
print("NO ORDERS WILL BE SENT.")
print("==========================================\n")


try:
    client.start()
    client.run_until_disconnected()

finally:
    client.disconnect()