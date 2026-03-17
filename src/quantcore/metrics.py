"""Performance metrics for backtest results."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_metrics(results: pd.DataFrame, initial_capital: float = 100_000) -> dict:
    """Compute standard performance metrics from backtest results.

    Parameters
    ----------
    results : pd.DataFrame
        Backtest results with at least ``portfolio`` and ``trades`` columns.
    initial_capital : float
        The starting portfolio value.

    Returns
    -------
    dict
        Dictionary with sharpe_ratio, max_drawdown, cagr, win_rate, and more.
    """
    portfolio = results["portfolio"].values
    final_value = portfolio[-1]
    total_return = (final_value - initial_capital) / initial_capital

    # Daily returns
    daily_returns = np.diff(portfolio) / portfolio[:-1]
    daily_returns = daily_returns[np.isfinite(daily_returns)]

    # Sharpe ratio (annualized, assuming 252 trading days)
    if len(daily_returns) > 1 and np.std(daily_returns) > 0:
        sharpe_ratio = (np.mean(daily_returns) / np.std(daily_returns)) * np.sqrt(252)
    else:
        sharpe_ratio = 0.0

    # Max drawdown
    cumulative_max = np.maximum.accumulate(portfolio)
    drawdowns = (portfolio - cumulative_max) / cumulative_max
    max_drawdown = float(np.min(drawdowns))

    # CAGR
    n_days = len(portfolio)
    n_years = n_days / 252 if n_days > 0 else 1
    if initial_capital > 0 and final_value > 0 and n_years > 0:
        cagr = (final_value / initial_capital) ** (1 / n_years) - 1
    else:
        cagr = 0.0

    # Win rate
    trades = results["trades"].values
    buy_indices = np.where(trades == 1)[0]
    sell_indices = np.where(trades == -1)[0]
    n_trades = min(len(buy_indices), len(sell_indices))
    wins = 0
    for i in range(n_trades):
        buy_price = results["close"].iloc[buy_indices[i]]
        sell_price = results["close"].iloc[sell_indices[i]]
        if sell_price > buy_price:
            wins += 1
    win_rate = wins / n_trades if n_trades > 0 else 0.0

    return {
        "initial_capital": initial_capital,
        "final_value": final_value,
        "total_return": total_return,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "cagr": cagr,
        "win_rate": win_rate,
        "total_trades": n_trades,
        "winning_trades": wins,
        "losing_trades": n_trades - wins,
    }
