"""Moving Average Crossover strategy — buy on golden cross, sell on death cross."""

from __future__ import annotations

import pandas as pd

from quantcore.strategies.base import Strategy


class MovingAverageCrossover(Strategy):
    """Buy when the short-period MA crosses above the long-period MA,
    sell when it crosses below.

    Parameters
    ----------
    short_window : int
        Short moving average period (default 20).
    long_window : int
        Long moving average period (default 50).
    """

    name = "Moving Average Crossover"

    def __init__(self, short_window: int = 20, long_window: int = 50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        short_ma = close.rolling(self.short_window).mean()
        long_ma = close.rolling(self.long_window).mean()

        signals = pd.Series(0, index=data.index)
        signals[short_ma > long_ma] = 1
        signals[short_ma < long_ma] = -1
        signals.iloc[: self.long_window] = 0
        return signals
