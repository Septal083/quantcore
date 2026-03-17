"""QuantCore — open-core backtesting framework for quantitative trading strategies."""

__version__ = "0.1.0"

from quantcore.engine import Backtest
from quantcore.metrics import compute_metrics
from quantcore.strategies import MeanReversion, MomentumStrategy, MovingAverageCrossover

__all__ = [
    "Backtest",
    "compute_metrics",
    "MomentumStrategy",
    "MeanReversion",
    "MovingAverageCrossover",
]
