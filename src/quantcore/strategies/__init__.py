"""Built-in free trading strategies."""

from quantcore.strategies.mean_reversion import MeanReversion
from quantcore.strategies.momentum import MomentumStrategy
from quantcore.strategies.moving_average import MovingAverageCrossover

FREE_STRATEGIES = {
    "momentum": MomentumStrategy,
    "mean_reversion": MeanReversion,
    "moving_average": MovingAverageCrossover,
}

__all__ = [
    "MomentumStrategy",
    "MeanReversion",
    "MovingAverageCrossover",
    "FREE_STRATEGIES",
]
