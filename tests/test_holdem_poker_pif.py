from __future__ import annotations

from typing import Any
from unittest.mock import Mock

from pifs.holdem_poker_pif import HoldemPoker


def test_init_creates_flop_turn_river(base_pif_kwargs: dict[str, Any]) -> None:
    pif = HoldemPoker(**base_pif_kwargs)
    assert "FlopCards" in pif.pifOptions
    assert "TurnCard" in pif.pifOptions
    assert "RiverCard" in pif.pifOptions
    assert len(pif.pifOptions["FlopCards"]) == 3


def test_init_creates_hands(base_pif_kwargs: dict[str, Any]) -> None:
    pif = HoldemPoker(**base_pif_kwargs)
    assert "hands" in pif.pifOptions
    assert len(pif.pifOptions["hands"]) > 0


def test_handle_entry_pops_a_hand(base_pif_kwargs: dict[str, Any]) -> None:
    pif = HoldemPoker(**base_pif_kwargs)
    initial_hands = pif.pifOptions["hands"]
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    pif.handle_entry(comment, user, ["latherbot", "in"])
    assert len(pif.pifOptions["hands"]) < len(initial_hands)
    entry = pif.pifEntries["p1"]
    assert isinstance(entry, dict)
    assert len(entry["UserHoleCards"]) == 2
