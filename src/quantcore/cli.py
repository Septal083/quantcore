"""Command-line interface for QuantCore."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from quantcore.engine import Backtest
from quantcore.strategies import FREE_STRATEGIES


def _get_all_strategies() -> dict:
    """Return combined dict of free + pro strategies (pro only if licensed)."""
    all_strats = dict(FREE_STRATEGIES)
    try:
        from quantcore.pro.license import validate_license

        if validate_license():
            from quantcore.pro.strategies import PRO_STRATEGIES

            all_strats.update(PRO_STRATEGIES)
    except Exception:
        pass
    return all_strats


def cmd_backtest(args: argparse.Namespace) -> None:
    """Run a backtest from the CLI."""
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}")
        sys.exit(1)

    data = pd.read_csv(data_path, parse_dates=True, index_col=0)

    all_strategies = _get_all_strategies()
    strategy_key = args.strategy.lower().replace("-", "_").replace(" ", "_")

    if strategy_key not in all_strategies:
        # Check if it's a pro strategy that requires license
        from quantcore.pro.strategies import PRO_STRATEGIES

        if strategy_key in PRO_STRATEGIES:
            from quantcore.pro.license import require_pro

            if not require_pro():
                sys.exit(0)
            all_strategies.update(PRO_STRATEGIES)
        else:
            available = ", ".join(sorted(all_strategies.keys()))
            print(f"Error: Unknown strategy '{args.strategy}'. Available: {available}")
            sys.exit(1)

    strategy_cls = all_strategies[strategy_key]
    strategy = strategy_cls()

    bt = Backtest(
        data,
        strategy,
        initial_capital=args.capital,
        commission=args.commission,
    )
    bt.run()

    print(bt.summary())
    print()

    if args.output:
        out_path = bt.export_csv(args.output)
        print(f"Results exported to: {out_path}")

    if args.tearsheet:
        from quantcore.pro.license import require_pro

        if require_pro():
            from quantcore.pro.monte_carlo import monte_carlo_simulation
            from quantcore.pro.tearsheet import generate_tearsheet

            mc = monte_carlo_simulation(bt.results, initial_capital=args.capital)
            pdf_path = generate_tearsheet(
                bt.results, bt.metrics, mc, strategy.name, args.tearsheet
            )
            print(f"Tearsheet saved to: {pdf_path}")

    if args.monte_carlo:
        from quantcore.pro.license import require_pro

        if require_pro():
            from quantcore.pro.monte_carlo import monte_carlo_simulation

            mc = monte_carlo_simulation(
                bt.results, n_simulations=args.mc_runs, initial_capital=args.capital
            )
            ci = mc["confidence_intervals"]
            print(f"\nMonte Carlo ({mc['n_simulations']} simulations):")
            print(f"  Median final value: ${mc['median_final']:,.2f}")
            print(f"  Mean final value:   ${mc['mean_final']:,.2f}")
            for pct, val in ci.items():
                print(f"  {pct} percentile:    ${val:,.2f}")


def cmd_strategies(args: argparse.Namespace) -> None:
    """List available strategies."""
    print("Free strategies:")
    for name in sorted(FREE_STRATEGIES.keys()):
        print(f"  - {name}")

    print("\nPro strategies (requires license):")
    from quantcore.pro.strategies import PRO_STRATEGIES

    for name in sorted(PRO_STRATEGIES.keys()):
        print(f"  - {name}")


def cmd_optimize(args: argparse.Namespace) -> None:
    """Run parameter grid search optimization."""
    from quantcore.pro.license import require_pro

    if not require_pro():
        sys.exit(0)

    from quantcore.pro.optimizer import grid_search

    data = pd.read_csv(args.data, parse_dates=True, index_col=0)

    all_strategies = dict(FREE_STRATEGIES)
    from quantcore.pro.strategies import PRO_STRATEGIES

    all_strategies.update(PRO_STRATEGIES)

    strategy_key = args.strategy.lower().replace("-", "_").replace(" ", "_")
    if strategy_key not in all_strategies:
        print(f"Error: Unknown strategy '{args.strategy}'")
        sys.exit(1)

    # Default param grids per strategy
    default_grids = {
        "momentum": {"lookback": [10, 20, 30, 50]},
        "mean_reversion": {"window": [10, 20, 30], "threshold": [1.0, 1.5, 2.0]},
        "moving_average": {"short_window": [10, 20], "long_window": [30, 50, 100]},
        "rsi": {"period": [7, 14, 21], "oversold": [20, 30], "overbought": [70, 80]},
        "bollinger_bands": {"window": [10, 20, 30], "num_std": [1.5, 2.0, 2.5]},
        "macd": {"fast": [8, 12], "slow": [21, 26], "signal": [7, 9]},
    }

    param_grid = default_grids.get(strategy_key, {"lookback": [10, 20, 30]})
    results = grid_search(data, all_strategies[strategy_key], param_grid, metric=args.metric)

    print(f"\nGrid search results for {strategy_key} (optimizing {args.metric}):\n")
    for i, r in enumerate(results[:10]):
        print(f"  #{i + 1}: {r['params']} -> {args.metric}={r['score']:.4f}")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="quantcore",
        description="QuantCore — backtesting framework for quantitative trading strategies",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # backtest
    bt_parser = subparsers.add_parser("backtest", help="Run a backtest")
    bt_parser.add_argument("--data", "-d", required=True, help="Path to OHLCV CSV file")
    bt_parser.add_argument(
        "--strategy", "-s", required=True, help="Strategy name (e.g. momentum, mean_reversion)"
    )
    bt_parser.add_argument("--capital", "-c", type=float, default=100_000, help="Initial capital")
    bt_parser.add_argument("--commission", type=float, default=0.001, help="Commission rate")
    bt_parser.add_argument("--output", "-o", help="Output CSV path for results")
    bt_parser.add_argument("--tearsheet", help="Output PDF path for tearsheet (Pro)")
    bt_parser.add_argument("--monte-carlo", action="store_true", help="Run Monte Carlo sim (Pro)")
    bt_parser.add_argument("--mc-runs", type=int, default=1000, help="Number of MC simulations")

    # strategies
    subparsers.add_parser("strategies", help="List available strategies")

    # optimize
    opt_parser = subparsers.add_parser("optimize", help="Grid search optimization (Pro)")
    opt_parser.add_argument("--data", "-d", required=True, help="Path to OHLCV CSV file")
    opt_parser.add_argument("--strategy", "-s", required=True, help="Strategy to optimize")
    opt_parser.add_argument("--metric", "-m", default="sharpe_ratio", help="Metric to optimize")

    return parser


def main(argv: list[str] | None = None) -> None:
    """Entry point for the quantcore CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "backtest": cmd_backtest,
        "strategies": cmd_strategies,
        "optimize": cmd_optimize,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
