"""Parameter grid search optimizer for strategy tuning."""

from __future__ import annotations

import itertools
from typing import Any

import pandas as pd

from quantcore.engine import Backtest
from quantcore.metrics import compute_metrics


def grid_search(
    data: pd.DataFrame,
    strategy_class,
    param_grid: dict[str, list],
    initial_capital: float = 100_000,
    metric: str = "sharpe_ratio",
) -> list[dict[str, Any]]:
    """Run a grid search over strategy parameters and rank by a metric.

    Parameters
    ----------
    data : pd.DataFrame
        OHLCV data for backtesting.
    strategy_class : type
        Strategy class to instantiate with each parameter combination.
    param_grid : dict
        Mapping of parameter names to lists of values to try.
    initial_capital : float
        Starting portfolio value.
    metric : str
        Metric to optimize (default ``sharpe_ratio``).

    Returns
    -------
    list[dict]
        Sorted list of results, best first. Each dict contains ``params``,
        ``metrics``, and the target ``score``.
    """
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    results = []

    for combo in itertools.product(*values):
        params = dict(zip(keys, combo))
        try:
            strategy = strategy_class(**params)
            bt = Backtest(data.copy(), strategy, initial_capital=initial_capital)
            bt_results = bt.run()
            m = compute_metrics(bt_results, initial_capital)
            results.append({
                "params": params,
                "metrics": m,
                "score": m.get(metric, 0),
            })
        except Exception:
            results.append({
                "params": params,
                "metrics": {},
                "score": float("-inf"),
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
