from __future__ import annotations
import os
from typing import List
from ..utils.validators import COINLIST_DIR


def load_symbols(exchange: str) -> List[str]:
    """Load symbols for a given exchange, with multiple fallback strategies."""
    # Try multiple possible paths
    possible_paths = [
        os.path.join(COINLIST_DIR, f"{exchange}.txt"),
        os.path.join(COINLIST_DIR, f"{exchange.lower()}.txt"),
        # Fallback: relative to this file
        os.path.join(os.path.dirname(__file__), "..", "..", "coinlist", f"{exchange}.txt"),
        # Another fallback
        os.path.join(os.path.dirname(__file__), "..", "..", "coinlist", f"{exchange.lower()}.txt")
    ]
    
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                symbols = [line.strip() for line in content.split('\n') if line.strip()]
                if symbols:  # Only return if we actually got symbols
                    return symbols
        except (FileNotFoundError, IOError, UnicodeDecodeError):
            continue
    
    # If all fails, return empty list
    return []
