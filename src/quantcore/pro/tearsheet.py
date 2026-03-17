"""Tearsheet PDF generator — professional-layout backtest report."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages


def generate_tearsheet(
    results,
    metrics: dict,
    monte_carlo: Optional[dict] = None,
    strategy_name: str = "Strategy",
    output_path: Union[str, Path] = "tearsheet.pdf",
) -> Path:
    """Generate a professional tearsheet PDF.

    Parameters
    ----------
    results : pd.DataFrame
        Backtest results with ``portfolio``, ``close``, and ``trades`` columns.
    metrics : dict
        Performance metrics from ``compute_metrics``.
    monte_carlo : dict, optional
        Monte Carlo simulation results.
    strategy_name : str
        Name of the strategy for the report title.
    output_path : str or Path
        Output PDF file path.

    Returns
    -------
    Path
        Path to the generated PDF.
    """
    output_path = Path(output_path)

    with PdfPages(output_path) as pdf:
        # Page 1: Equity curve and drawdown
        fig, axes = plt.subplots(3, 1, figsize=(11, 14))
        fig.suptitle(f"QuantCore Tearsheet — {strategy_name}", fontsize=16, fontweight="bold")

        # Equity curve
        ax = axes[0]
        ax.plot(results["portfolio"].values, color="#2196F3", linewidth=1.2)
        ax.set_title("Equity Curve", fontsize=12)
        ax.set_ylabel("Portfolio Value ($)")
        ax.grid(True, alpha=0.3)

        # Drawdown
        portfolio = results["portfolio"].values
        cummax = np.maximum.accumulate(portfolio)
        drawdown = (portfolio - cummax) / cummax
        ax = axes[1]
        ax.fill_between(range(len(drawdown)), drawdown, 0, color="#F44336", alpha=0.4)
        ax.set_title("Drawdown", fontsize=12)
        ax.set_ylabel("Drawdown (%)")
        ax.grid(True, alpha=0.3)

        # Daily returns distribution
        daily_returns = np.diff(portfolio) / portfolio[:-1]
        ax = axes[2]
        ax.hist(daily_returns, bins=50, color="#4CAF50", alpha=0.7, edgecolor="white")
        ax.set_title("Daily Returns Distribution", fontsize=12)
        ax.set_xlabel("Daily Return")
        ax.set_ylabel("Frequency")
        ax.grid(True, alpha=0.3)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        pdf.savefig(fig)
        plt.close(fig)

        # Page 2: Metrics table and Monte Carlo (if available)
        fig, axes = plt.subplots(2, 1, figsize=(11, 14))
        fig.suptitle("Performance Summary", fontsize=16, fontweight="bold")

        # Metrics table
        ax = axes[0]
        ax.axis("off")
        table_data = [
            ["Metric", "Value"],
            ["Initial Capital", f"${metrics['initial_capital']:,.2f}"],
            ["Final Value", f"${metrics['final_value']:,.2f}"],
            ["Total Return", f"{metrics['total_return']:.2%}"],
            ["CAGR", f"{metrics['cagr']:.2%}"],
            ["Sharpe Ratio", f"{metrics['sharpe_ratio']:.4f}"],
            ["Max Drawdown", f"{metrics['max_drawdown']:.2%}"],
            ["Win Rate", f"{metrics['win_rate']:.2%}"],
            ["Total Trades", f"{metrics['total_trades']}"],
        ]
        table = ax.table(
            cellText=table_data[1:],
            colLabels=table_data[0],
            loc="center",
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.8)

        # Monte Carlo visualization
        ax = axes[1]
        if monte_carlo is not None:
            sims = monte_carlo["simulations"]
            n_show = min(100, sims.shape[0])
            for i in range(n_show):
                ax.plot(sims[i], alpha=0.05, color="#2196F3", linewidth=0.5)
            ci = monte_carlo["confidence_intervals"]
            ax.set_title(
                f"Monte Carlo ({monte_carlo['n_simulations']} runs) — "
                f"95% CI: ${ci['5%']:,.0f} to ${ci['95%']:,.0f}",
                fontsize=11,
            )
            ax.set_ylabel("Portfolio Value ($)")
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, "Monte Carlo not available", ha="center", va="center", fontsize=14)
            ax.axis("off")

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        pdf.savefig(fig)
        plt.close(fig)

    return output_path
