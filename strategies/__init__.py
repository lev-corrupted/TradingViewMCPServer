"""
Forex Trading Strategies Package

This package contains all trading strategies for the backtesting system.
Each strategy inherits from BaseStrategy and can be auto-discovered by the system.
"""

from pathlib import Path
import importlib.util
import inspect
from typing import List, Type

def discover_strategies() -> dict:
    """
    Auto-discover all strategy classes in the strategies folder.

    Returns:
        dict: Dictionary mapping strategy names to strategy classes
    """
    strategies = {}
    strategies_dir = Path(__file__).parent

    # Iterate through all Python files in the strategies directory
    for strategy_file in strategies_dir.glob("*.py"):
        if strategy_file.name.startswith("_") or strategy_file.name in ["base_strategy.py", "template.py"]:
            continue

        # Import the module
        module_name = strategy_file.stem
        spec = importlib.util.spec_from_file_location(module_name, strategy_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find all Strategy classes in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it's a Strategy class (but not the base class)
                if hasattr(obj, '__bases__'):
                    base_names = [base.__name__ for base in obj.__bases__]
                    if 'BaseStrategy' in base_names or 'Strategy' in base_names:
                        if name not in ['BaseStrategy', 'Strategy']:
                            strategies[name] = obj

    return strategies

__all__ = ['discover_strategies']