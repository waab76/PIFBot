from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from pifs.infinite_poker_pif import InfinitePoker


def test_handle_entry_deals_five_cards(base_pif_kwargs: dict[str, Any]) -> None:
    pif = InfinitePoker(**base_pif_kwargs)
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    pif.handle_entry(comment, user, ["latherbot", "in"])
    entry = pif.pifEntries["p1"]
    assert isinstance(entry, dict)
    assert len(entry["UserHand"]) == 5


def test_handle_entry_has_hand_score(base_pif_kwargs: dict[str, Any]) -> None:
    pif = InfinitePoker(**base_pif_kwargs)
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    pif.handle_entry(comment, user, ["latherbot", "in"])
    entry = pif.pifEntries["p1"]
    assert isinstance(entry, dict)
    assert entry["HandScore"] > 0
