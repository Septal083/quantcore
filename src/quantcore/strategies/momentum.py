"""Momentum strategy — buy when price is trending up over a lookback window."""

from __future__ import annotations

import pandas as pd

from quantcore.strategies.base import Strategy


class MomentumStrategy(Strategy):
    """Buy when the rate of change over ``lookback`` periods is positive,
    sell when it turns negative.

    Parameters
    ----------
    lookback : int
        Number of periods for momentum calculation (default 20).
    """

    name = "Momentum"

    def __init__(self, lookback: int = 20):
        self.lookback = lookback

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        momentum = close.pct_change(self.lookback)
        signals = pd.Series(0, index=data.index)
        signals[momentum > 0] = 1
        signals[momentum < 0] = -1
        signals.iloc[: self.lookback] = 0
        return signals
