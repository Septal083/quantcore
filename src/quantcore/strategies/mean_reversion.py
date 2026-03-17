"""Mean Reversion strategy — buy when price dips below its moving average, sell above."""

from __future__ import annotations

import pandas as pd

from quantcore.strategies.base import Strategy


class MeanReversion(Strategy):
    """Buy when price falls ``threshold`` standard deviations below its rolling mean,
    sell when it returns above the mean.

    Parameters
    ----------
    window : int
        Rolling window for mean and std (default 20).
    threshold : float
        Number of standard deviations for entry signal (default 1.5).
    """

    name = "Mean Reversion"

    def __init__(self, window: int = 20, threshold: float = 1.5):
        self.window = window
        self.threshold = threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        rolling_mean = close.rolling(self.window).mean()
        rolling_std = close.rolling(self.window).std()

        signals = pd.Series(0, index=data.index)
        lower = rolling_mean - self.threshold * rolling_std
        signals[close < lower] = 1
        signals[close > rolling_mean] = -1
        signals.iloc[: self.window] = 0
        return signals
