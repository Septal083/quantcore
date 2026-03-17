"""Pro trading strategies — 10 additional strategies for QuantCore Pro users."""

from __future__ import annotations

import numpy as np
import pandas as pd

from quantcore.strategies.base import Strategy


class RSIStrategy(Strategy):
    """Relative Strength Index — buy on oversold, sell on overbought."""

    name = "RSI"

    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(self.period).mean()
        loss = (-delta.clip(upper=0)).rolling(self.period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))

        signals = pd.Series(0, index=data.index)
        signals[rsi < self.oversold] = 1
        signals[rsi > self.overbought] = -1
        signals.iloc[: self.period + 1] = 0
        return signals


class BollingerBandsStrategy(Strategy):
    """Bollinger Bands — buy below lower band, sell above upper band."""

    name = "Bollinger Bands"

    def __init__(self, window: int = 20, num_std: float = 2.0):
        self.window = window
        self.num_std = num_std

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        sma = close.rolling(self.window).mean()
        std = close.rolling(self.window).std()
        upper = sma + self.num_std * std
        lower = sma - self.num_std * std

        signals = pd.Series(0, index=data.index)
        signals[close < lower] = 1
        signals[close > upper] = -1
        signals.iloc[: self.window] = 0
        return signals


class MACDStrategy(Strategy):
    """MACD — buy when MACD crosses above signal line, sell on cross below."""

    name = "MACD"

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        ema_fast = close.ewm(span=self.fast, adjust=False).mean()
        ema_slow = close.ewm(span=self.slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()

        signals = pd.Series(0, index=data.index)
        signals[(macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))] = 1
        signals[(macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))] = -1
        warmup = self.slow + self.signal_period
        signals.iloc[:warmup] = 0
        return signals


class PairsTradingStrategy(Strategy):
    """Pairs Trading — trade the spread between close and a synthetic pair (rolling ratio)."""

    name = "Pairs Trading"

    def __init__(self, window: int = 30, entry_z: float = 2.0, exit_z: float = 0.5):
        self.window = window
        self.entry_z = entry_z
        self.exit_z = exit_z

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        rolling_mean = close.rolling(self.window).mean()
        spread = close - rolling_mean
        spread_mean = spread.rolling(self.window).mean()
        spread_std = spread.rolling(self.window).std()
        z_score = (spread - spread_mean) / spread_std.replace(0, np.nan)

        signals = pd.Series(0, index=data.index)
        signals[z_score < -self.entry_z] = 1
        signals[z_score > self.entry_z] = -1
        signals[z_score.abs() < self.exit_z] = 0
        signals.iloc[: self.window * 2] = 0
        return signals


class VolatilityBreakoutStrategy(Strategy):
    """Volatility Breakout — buy on upside breakout, sell on downside breakout."""

    name = "Volatility Breakout"

    def __init__(self, window: int = 20, multiplier: float = 1.5):
        self.window = window
        self.multiplier = multiplier

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        atr = (data["high"] - data["low"]).rolling(self.window).mean()
        rolling_mean = close.rolling(self.window).mean()
        upper = rolling_mean + self.multiplier * atr
        lower = rolling_mean - self.multiplier * atr

        signals = pd.Series(0, index=data.index)
        signals[close > upper] = 1
        signals[close < lower] = -1
        signals.iloc[: self.window] = 0
        return signals


class TurtleTradingStrategy(Strategy):
    """Turtle Trading — buy at highest high, sell at lowest low over lookback."""

    name = "Turtle Trading"

    def __init__(self, entry_window: int = 20, exit_window: int = 10):
        self.entry_window = entry_window
        self.exit_window = exit_window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        high_max = data["high"].rolling(self.entry_window).max()
        low_min = data["low"].rolling(self.exit_window).min()

        signals = pd.Series(0, index=data.index)
        signals[data["close"] >= high_max] = 1
        signals[data["close"] <= low_min] = -1
        signals.iloc[: self.entry_window] = 0
        return signals


class MeanReversionZScore(Strategy):
    """Mean Reversion Z-Score — trade based on z-score of price relative to rolling stats."""

    name = "Mean Reversion Z-Score"

    def __init__(self, window: int = 30, entry_z: float = 2.0, exit_z: float = 0.5):
        self.window = window
        self.entry_z = entry_z
        self.exit_z = exit_z

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        mean = close.rolling(self.window).mean()
        std = close.rolling(self.window).std()
        z = (close - mean) / std.replace(0, np.nan)

        signals = pd.Series(0, index=data.index)
        signals[z < -self.entry_z] = 1
        signals[z > self.entry_z] = -1
        signals[z.abs() < self.exit_z] = 0
        signals.iloc[: self.window] = 0
        return signals


class KalmanFilterStrategy(Strategy):
    """Kalman Filter — use a simple Kalman filter to estimate trend and trade on deviations."""

    name = "Kalman Filter"

    def __init__(self, process_noise: float = 0.01, measurement_noise: float = 1.0):
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"].values
        n = len(close)

        # Simple 1D Kalman filter
        estimate = np.zeros(n)
        estimate[0] = close[0]
        error_cov = 1.0

        for i in range(1, n):
            # Predict
            pred = estimate[i - 1]
            pred_cov = error_cov + self.process_noise

            # Update
            kalman_gain = pred_cov / (pred_cov + self.measurement_noise)
            estimate[i] = pred + kalman_gain * (close[i] - pred)
            error_cov = (1 - kalman_gain) * pred_cov

        signals = pd.Series(0, index=data.index)
        diff = close - estimate
        std_diff = np.std(diff[20:]) if n > 20 else 1.0
        if std_diff > 0:
            signals[diff > std_diff] = -1
            signals[diff < -std_diff] = 1
        signals.iloc[:20] = 0
        return signals


class DualMomentumStrategy(Strategy):
    """Dual Momentum — combine absolute and relative momentum signals."""

    name = "Dual Momentum"

    def __init__(self, lookback: int = 60, short_lookback: int = 20):
        self.lookback = lookback
        self.short_lookback = short_lookback

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        abs_momentum = close.pct_change(self.lookback)
        rel_momentum = close.pct_change(self.short_lookback)

        signals = pd.Series(0, index=data.index)
        signals[(abs_momentum > 0) & (rel_momentum > 0)] = 1
        signals[(abs_momentum < 0) & (rel_momentum < 0)] = -1
        signals.iloc[: self.lookback] = 0
        return signals


class SectorRotationStrategy(Strategy):
    """Sector Rotation — rotate based on rolling performance rank (single-asset proxy)."""

    name = "Sector Rotation"

    def __init__(self, fast_window: int = 10, slow_window: int = 40):
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        close = data["close"]
        fast_ret = close.pct_change(self.fast_window)
        slow_ret = close.pct_change(self.slow_window)
        combined = 0.6 * fast_ret + 0.4 * slow_ret

        signals = pd.Series(0, index=data.index)
        median = combined.rolling(self.slow_window).median()
        signals[combined > median] = 1
        signals[combined < median] = -1
        signals.iloc[: self.slow_window * 2] = 0
        return signals


PRO_STRATEGIES = {
    "rsi": RSIStrategy,
    "bollinger_bands": BollingerBandsStrategy,
    "macd": MACDStrategy,
    "pairs_trading": PairsTradingStrategy,
    "volatility_breakout": VolatilityBreakoutStrategy,
    "turtle_trading": TurtleTradingStrategy,
    "mean_reversion_zscore": MeanReversionZScore,
    "kalman_filter": KalmanFilterStrategy,
    "dual_momentum": DualMomentumStrategy,
    "sector_rotation": SectorRotationStrategy,
}
