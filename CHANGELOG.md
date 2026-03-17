# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-17

### Added
- Backtesting engine with OHLCV DataFrame support
- 3 built-in strategies: Momentum, Mean Reversion, Moving Average Crossover
- Performance metrics: Sharpe ratio, max drawdown, CAGR, win rate
- CSV export of backtest results
- CLI interface: `quantcore backtest --data mydata.csv --strategy momentum`
- Pro features (license-gated via Polar.sh):
  - 10 additional strategies (RSI, Bollinger Bands, MACD, Pairs Trading, Volatility Breakout, Turtle Trading, Mean Reversion Z-Score, Kalman Filter, Dual Momentum, Sector Rotation)
  - Monte Carlo simulation with confidence intervals
  - Tearsheet PDF generator
  - Parameter grid search optimizer
