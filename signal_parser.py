import re
from dataclasses import dataclass
from typing import List


@dataclass
class ParsedSignal:
    symbol: str
    direction: str
    entry_low: float
    entry_high: float
    take_profits: List[float]
    stop_loss: float


def parse_signal(text: str) -> ParsedSignal | None:
    """
    Parse an XNINE XAU algo signal.

    Expected format:

    Algorithm is buying/selling XAUUSD

    📍PRICE - PRICE

    TP 1: PRICE
    TP 2: PRICE
    TP 3: PRICE
    TP 4: PRICE
    TP 5: PRICE

    SL: PRICE
    """

    if not text or not text.strip():
        print("ERROR: Empty signal.")
        return None

    # --------------------------------------------------
    # Direction + symbol
    # --------------------------------------------------

    direction_match = re.search(
        r"Algorithm\s+is\s+(buying|selling)\s+(XAUUSD)",
        text,
        re.IGNORECASE,
    )

    if not direction_match:
        print("ERROR: Could not find BUY/SELL XAUUSD signal.")
        return None

    direction_word = direction_match.group(1).lower()
    symbol = direction_match.group(2).upper()

    if direction_word == "buying":
        direction = "BUY"
    else:
        direction = "SELL"


    # --------------------------------------------------
    # Entry zone
    # --------------------------------------------------

    entry_match = re.search(
        r"📍\s*([\d.]+)\s*-\s*([\d.]+)",
        text,
    )

    if not entry_match:
        print("ERROR: Could not find entry zone.")
        return None

    entry_1 = float(entry_match.group(1))
    entry_2 = float(entry_match.group(2))

    # Normalize the zone
    entry_low = min(entry_1, entry_2)
    entry_high = max(entry_1, entry_2)

    # --------------------------------------------------
    # Take profits
    # --------------------------------------------------

    tp_matches = re.findall(
        r"TP\s*[1-5]\s*:\s*([\d.]+)",
        text,
        re.IGNORECASE,
    )

    if len(tp_matches) != 5:
        print(
            f"ERROR: Expected 5 take profits, "
            f"found {len(tp_matches)}."
        )
        return None

    take_profits = [float(tp) for tp in tp_matches]

    # --------------------------------------------------
    # Stop loss
    # --------------------------------------------------

    sl_match = re.search(
        r"SL\s*:\s*([\d.]+)",
        text,
        re.IGNORECASE,
    )

    if not sl_match:
        print("ERROR: Could not find stop loss.")
        return None

    stop_loss = float(sl_match.group(1))

    # --------------------------------------------------
    # Return parsed signal
    # --------------------------------------------------

    return ParsedSignal(
        symbol=symbol,
        direction=direction,
        entry_low=entry_low,
        entry_high=entry_high,
        take_profits=take_profits,
        stop_loss=stop_loss,
    )


def print_signal(signal: ParsedSignal):
    """Print a parsed signal in a readable format."""

    print("\n========== PARSED SIGNAL ==========")
    print(f"Symbol:      {signal.symbol}")
    print(f"Direction:   {signal.direction}")
    print(f"Entry low:   {signal.entry_low}")
    print(f"Entry high:  {signal.entry_high}")

    print("\nTake profits:")
    for index, tp in enumerate(signal.take_profits, start=1):
        print(f"  TP{index}: {tp}")

    print(f"\nStop loss:   {signal.stop_loss}")
    print("===================================\n")


if __name__ == "__main__":

    test_signals = [
        """
        Algorithm is selling XAUUSD

        📍4155.09 - 4162.78

        ✅ TP 1: 4151.24

        ✅ TP 2: 4147.4

        ✅ TP 3: 4139.71

        ✅ TP 4: 4124.32

        ✅ TP 5: 4093.55

        ❗️ SL: 4178.17

        #algoxnine
        """,

        """
        Algorithm is buying XAUUSD

        📍4156.66 - 4149.24

        ✅ TP 1: 4160.37

        ✅ TP 2: 4164.08

        ✅ TP 3: 4171.51

        ✅ TP 4: 4186.36

        ✅ TP 5: 4216.05

        ❗️ SL: 4134.39

        #algoxnine
        """,

        """
        Algorithm is selling XAUUSD

        📍4179.02 - 4185.41

        ✅ TP 1: 4175.83

        ✅ TP 2: 4172.63

        ✅ TP 3: 4166.24

        ✅ TP 4: 4153.47

        ✅ TP 5: 4127.92

        ❗️ SL: 4198.18

        #algoxnine
        """,

        """
        Algorithm is buying XAUUSD

        📍4182.69 - 4176.24

        ✅ TP 1: 4185.92

        ✅ TP 2: 4189.14

        ✅ TP 3: 4195.6

        ✅ TP 4: 4208.5

        ✅ TP 5: 4234.31

        ❗️ SL: 4163.33

        #algoxnine
        """,

        """
        Algorithm is selling XAUUSD

        📍4172.62 - 4178.69

        ✅ TP 1: 4169.59

        ✅ TP 2: 4166.55

        ✅ TP 3: 4160.48

        ✅ TP 4: 4148.34

        ✅ TP 5: 4124.07

        ❗️ SL: 4190.83

        #algoxnine
        """,
    ]

    print("\n========================================")
    print("TESTING XNINE SIGNAL PARSER")
    print("========================================")

    successful = 0

    for number, text in enumerate(test_signals, start=1):

        print(f"\n---------- SIGNAL {number} ----------")

        signal = parse_signal(text)

        if signal is None:
            print("RESULT: FAILED")
            continue

        print_signal(signal)
        successful += 1

    print("\n========================================")
    print(f"RESULT: {successful}/{len(test_signals)} SIGNALS PARSED")
    print("========================================")