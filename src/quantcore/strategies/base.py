"""Base class for all trading strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Strategy(ABC):
    """Abstract base for trading strategies.

    Subclasses must implement ``generate_signals`` which returns a Series of
    +1 (buy), -1 (sell), or 0 (hold) for each row in the input data.
    """

    name: str = "BaseStrategy"

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate trading signals from OHLCV data.

        Parameters
        ----------
        data : pd.DataFrame
            OHLCV DataFrame with lowercase column names.

        Returns
        -------
        pd.Series
            Signal series with values in {-1, 0, 1}.
        """
        ...
