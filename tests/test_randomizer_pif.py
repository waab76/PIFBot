from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import pytest

from config import bot_name
from pifs.randomizer_pif import Randomizer


@pytest.fixture
def randomizer(base_pif_kwargs: dict[str, Any]) -> Randomizer:
    return Randomizer(**base_pif_kwargs)


def test_pif_type(randomizer: Randomizer) -> None:
    assert randomizer.pif_type == "randomizer"


def test_handle_entry_stores_comment_id(randomizer: Randomizer) -> None:
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    randomizer.handle_entry(comment, user, [bot_name.lower(), "in"])
    assert randomizer.pifEntries["p1"] == "c1"


def test_determine_winner_shuffles_and_stores_list(randomizer: Randomizer) -> None:
    randomizer.pifEntries = {"p1": "c1", "p2": "c2", "p3": "c3"}
    with patch("random.shuffle", side_effect=lambda x: x.reverse()):
        randomizer.determine_winner()
    assert isinstance(randomizer.pifWinner, list)
    assert "p3" in randomizer.pifWinner


def test_generate_winner_comment(randomizer: Randomizer) -> None:
    randomizer.pifEntries = {"p1": "c1", "p2": "c2"}
    randomizer.pifWinner = ["p2", "p1"]  # type: ignore[assignment]
    comment = randomizer.generate_winner_comment()
    assert "p2" in comment
    assert "p1" in comment
