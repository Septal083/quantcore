[![PyPI version](https://img.shields.io/pypi/v/quantcore-lite)](https://pypi.org/project/quantcore-lite/)
[![GitHub stars](https://img.shields.io/github/stars/Septal083/quantcore)](https://github.com/Septal083/quantcore/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# QuantCore

**Open-core backtesting framework for quantitative trading strategies.**

QuantCore lets you backtest trading strategies against historical OHLCV data with a clean Python API and CLI. The free tier includes three battle-tested strategies and essential performance metrics. Upgrade to Pro for advanced strategies, Monte Carlo simulation, tearsheet PDF reports, and parameter optimization.

## Installation

```bash
pip install quantcore-lite
```

## Quick Start

### Python API

```python
import pandas as pd
from quantcore import Backtest, MomentumStrategy

# Load your OHLCV data
data = pd.read_csv("market_data.csv", index_col=0, parse_dates=True)

# Run a backtest with the Momentum strategy
bt = Backtest(data, MomentumStrategy(lookback=20))
bt.run()

print(bt.summary())
bt.export_csv("results.csv")
```

### CLI

```bash
quantcore backtest --data market_data.csv --strategy momentum
quantcore backtest --data market_data.csv --strategy mean_reversion --output results.csv
quantcore strategies
```

## Strategies

### Momentum

Buy when the rate of change over a lookback period is positive, sell when negative.

```python
from quantcore import Backtest, MomentumStrategy

strategy = MomentumStrategy(lookback=20)
bt = Backtest(data, strategy)
bt.run()
print(bt.summary())
```

### Mean Reversion

Buy when price falls below its rolling mean by a threshold, sell when it reverts above.

```python
from quantcore import Backtest, MeanReversion

strategy = MeanReversion(window=20, threshold=1.5)
bt = Backtest(data, strategy)
bt.run()
print(bt.summary())
```

### Moving Average Crossover

Buy on golden cross (short MA crosses above long MA), sell on death cross.

```python
from quantcore import Backtest, MovingAverageCrossover

strategy = MovingAverageCrossover(short_window=20, long_window=50)
bt = Backtest(data, strategy)
bt.run()
print(bt.summary())
```

## Performance Metrics

Every backtest reports:

| Metric | Description |
|--------|-------------|
| **Sharpe Ratio** | Risk-adjusted return (annualized) |
| **Max Drawdown** | Largest peak-to-trough decline |
| **CAGR** | Compound annual growth rate |
| **Win Rate** | Percentage of profitable trades |
| **Total Return** | Overall portfolio return |

## Free vs Pro Comparison

| Feature | Free | Pro |
|---------|:----:|:---:|
| Momentum strategy | ✅ | ✅ |
| Mean Reversion strategy | ✅ | ✅ |
| Moving Average Crossover strategy | ✅ | ✅ |
| Performance metrics (Sharpe, CAGR, drawdown, win rate) | ✅ | ✅ |
| CSV export | ✅ | ✅ |
| CLI interface | ✅ | ✅ |
| RSI, Bollinger Bands, MACD strategies | ❌ | ✅ |
| Pairs Trading, Volatility Breakout, Turtle Trading | ❌ | ✅ |
| Mean Reversion Z-Score, Kalman Filter, Dual Momentum, Sector Rotation | ❌ | ✅ |
| Monte Carlo simulation (1000 runs, confidence intervals) | ❌ | ✅ |
| Tearsheet PDF generator | ❌ | ✅ |
| Parameter grid search optimizer | ❌ | ✅ |

## ⭐ Pro Version

Unlock 10 additional strategies, Monte Carlo simulation, tearsheet PDF reports, and parameter optimization.

**[Get QuantCore Pro →](YOUR_POLAR_LINK)**

Set your license key:

```bash
export QUANTCORE_LICENSE_KEY="your-license-key"
```

Then use Pro features:

```bash
quantcore backtest --data market_data.csv --strategy rsi --tearsheet report.pdf --monte-carlo
quantcore optimize --data market_data.csv --strategy bollinger_bands
```

Pro features are validated via [Polar.sh](https://polar.sh) license keys.

## License

MIT — see [LICENSE](LICENSE) for details.
