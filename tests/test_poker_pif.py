from __future__ import annotations

from typing import Any
from unittest.mock import Mock

from pifs.poker_pif import Poker


def test_init_creates_deck_and_shared_cards(base_pif_kwargs: dict[str, Any]) -> None:
    pif = Poker(**base_pif_kwargs)
    assert "Deck" in pif.pifOptions
    assert "SharedCards" in pif.pifOptions
    assert len(pif.pifOptions["SharedCards"]) == 3


def test_init_restores_from_options(base_pif_kwargs: dict[str, Any]) -> None:
    options = {
        "Deck": [[2, "♠"], [3, "♥"]],
        "SharedCards": [[10, "♥"], ["J", "♥"], ["Q", "♥"]],
    }
    pif = Poker(**{**base_pif_kwargs, "pifOptions": options})
    assert len(pif.pifOptions["Deck"]) == 2
    assert len(pif.pifOptions["SharedCards"]) == 3


def test_handle_entry_deals_two_cards(base_pif_kwargs: dict[str, Any]) -> None:
    pif = Poker(**base_pif_kwargs)
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    pif.handle_entry(comment, user, ["latherbot", "in"])
    assert "p1" in pif.pifEntries
    entry = pif.pifEntries["p1"]
    assert isinstance(entry, dict)
    assert len(entry["UserCards"]) == 2


def test_handle_entry_out_of_cards_finalizes(base_pif_kwargs: dict[str, Any]) -> None:
    options = {
        "Deck": [[2, "♠"]],
        "SharedCards": [[10, "♥"], ["J", "♥"], ["Q", "♥"]],
    }
    pif = Poker(**{**base_pif_kwargs, "pifOptions": options})
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    pif.finalize = Mock()  # type: ignore[method-assign]
    pif.handle_entry(comment, user, ["latherbot", "in"])
    pif.finalize.assert_called_once()
