from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from pifs.registry import known_pif_types


def test_known_pif_types_in_stats() -> None:
    types = known_pif_types()
    assert len(types) >= 9
    assert "lottery" in types
    assert "range" in types
    assert "poker" in types
    assert "geo" in types
    assert "battleship" in types
