"""Core backtesting engine that processes OHLCV data through trading strategies."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd

from quantcore.metrics import compute_metrics


class Backtest:
    """Run a strategy against historical OHLCV data and collect results.

    Parameters
    ----------
    data : pd.DataFrame
        OHLCV DataFrame with columns: open, high, low, close, volume.
        Index should be datetime or integer.
    strategy : object
        A strategy instance implementing ``generate_signals(data) -> pd.Series``.
    initial_capital : float
        Starting portfolio value (default 100_000).
    commission : float
        Per-trade commission as a fraction (default 0.001 = 0.1%).
    """

    def __init__(
        self,
        data: pd.DataFrame,
        strategy,
        initial_capital: float = 100_000,
        commission: float = 0.001,
    ):
        self.data = self._validate_data(data)
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.results: Optional[pd.DataFrame] = None
        self.metrics: Optional[dict] = None

    @staticmethod
    def _validate_data(data: pd.DataFrame) -> pd.DataFrame:
        required = {"open", "high", "low", "close", "volume"}
        columns_lower = {c.lower() for c in data.columns}
        missing = required - columns_lower
        if missing:
            raise ValueError(f"Missing required OHLCV columns: {missing}")
        data.columns = [c.lower() for c in data.columns]
        return data

    def run(self) -> pd.DataFrame:
        """Execute the backtest and return a results DataFrame."""
        signals = self.strategy.generate_signals(self.data)
        results = self._simulate(signals)
        self.results = results
        self.metrics = compute_metrics(results, self.initial_capital)
        return results

    def _simulate(self, signals: pd.Series) -> pd.DataFrame:
        """Simulate trades based on signals (+1 buy, -1 sell, 0 hold)."""
        prices = self.data["close"].values
        n = len(prices)

        positions = np.zeros(n)
        cash = np.full(n, self.initial_capital, dtype=float)
        holdings = np.zeros(n)
        portfolio = np.zeros(n)
        trades = np.zeros(n)

        sig = signals.values if hasattr(signals, "values") else np.asarray(signals)

        position = 0.0
        current_cash = self.initial_capital

        for i in range(n):
            price = prices[i]
            signal = sig[i] if i < len(sig) else 0

            if signal == 1 and position == 0:
                shares = int(current_cash * 0.95 / price)
                cost = shares * price * (1 + self.commission)
                if cost <= current_cash and shares > 0:
                    position = shares
                    current_cash -= cost
                    trades[i] = 1
            elif signal == -1 and position > 0:
                proceeds = position * price * (1 - self.commission)
                current_cash += proceeds
                trades[i] = -1
                position = 0

            positions[i] = position
            cash[i] = current_cash
            holdings[i] = position * price
            portfolio[i] = current_cash + position * price

        results = pd.DataFrame(
            {
                "close": prices,
                "signal": sig[:n] if len(sig) >= n else np.pad(sig, (0, n - len(sig))),
                "position": positions,
                "cash": cash,
                "holdings": holdings,
                "portfolio": portfolio,
                "trades": trades,
            },
            index=self.data.index,
        )
        return results

    def get_metrics(self) -> dict:
        """Return performance metrics. Runs backtest first if needed."""
        if self.metrics is None:
            self.run()
        return self.metrics

    def export_csv(self, path: Union[str, Path] = "backtest_results.csv") -> Path:
        """Export results to CSV."""
        if self.results is None:
            self.run()
        path = Path(path)
        self.results.to_csv(path)
        return path

    def summary(self) -> str:
        """Return a formatted summary of backtest metrics."""
        m = self.get_metrics()
        lines = [
            f"Strategy: {self.strategy.name}",
            f"Initial Capital: ${self.initial_capital:,.2f}",
            f"Final Value: ${m['final_value']:,.2f}",
            f"Total Return: {m['total_return']:.2%}",
            f"CAGR: {m['cagr']:.2%}",
            f"Sharpe Ratio: {m['sharpe_ratio']:.4f}",
            f"Max Drawdown: {m['max_drawdown']:.2%}",
            f"Win Rate: {m['win_rate']:.2%}",
            f"Total Trades: {m['total_trades']}",
        ]
        return "\n".join(lines)
