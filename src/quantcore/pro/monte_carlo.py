"""Monte Carlo simulation for backtest results."""

from __future__ import annotations

import numpy as np
import pandas as pd


def monte_carlo_simulation(
    results: pd.DataFrame,
    n_simulations: int = 1000,
    initial_capital: float = 100_000,
) -> dict:
    """Run Monte Carlo simulation by resampling daily returns.

    Parameters
    ----------
    results : pd.DataFrame
        Backtest results with a ``portfolio`` column.
    n_simulations : int
        Number of simulation runs (default 1000).
    initial_capital : float
        Starting portfolio value.

    Returns
    -------
    dict
        Contains ``simulations`` (array), ``confidence_intervals``, and summary stats.
    """
    portfolio = results["portfolio"].values
    daily_returns = np.diff(portfolio) / portfolio[:-1]
    daily_returns = daily_returns[np.isfinite(daily_returns)]
    n_days = len(daily_returns)

    if n_days == 0:
        return {
            "simulations": np.full((n_simulations, 1), initial_capital),
            "confidence_intervals": {},
            "median_final": initial_capital,
            "mean_final": initial_capital,
        }

    simulations = np.zeros((n_simulations, n_days + 1))
    simulations[:, 0] = initial_capital

    for i in range(n_simulations):
        sampled = np.random.choice(daily_returns, size=n_days, replace=True)
        simulations[i, 1:] = initial_capital * np.cumprod(1 + sampled)

    final_values = simulations[:, -1]

    ci = {
        "5%": float(np.percentile(final_values, 5)),
        "25%": float(np.percentile(final_values, 25)),
        "50%": float(np.percentile(final_values, 50)),
        "75%": float(np.percentile(final_values, 75)),
        "95%": float(np.percentile(final_values, 95)),
    }

    return {
        "simulations": simulations,
        "confidence_intervals": ci,
        "median_final": float(np.median(final_values)),
        "mean_final": float(np.mean(final_values)),
        "std_final": float(np.std(final_values)),
        "n_simulations": n_simulations,
    }
