from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import pytest

from pifs.battleship_pif import Battleship


@pytest.fixture
def battleship(base_pif_kwargs: dict[str, Any]) -> Battleship:
    return Battleship(**base_pif_kwargs)


def test_init_creates_board(battleship: Battleship) -> None:
    assert "Board" in battleship.pifOptions
    assert len(battleship.pifOptions["Board"]) == 26
    assert len(battleship.pifOptions["Board"][0]) == 26


def test_init_places_battleship(battleship: Battleship) -> None:
    board = battleship.pifOptions["Board"]
    b_count = sum(row.count("B") for row in board)
    assert b_count == 3


def test_init_restores_from_options(base_pif_kwargs: dict[str, Any]) -> None:
    board = [["." for _ in range(26)] for _ in range(26)]
    board[5][5] = "B"
    board[5][6] = "B"
    board[5][7] = "B"
    options = {
        "Board": board,
        "NorthSouth": 0,
        "StartRow": 5,
        "StartCol": 5,
    }
    b = Battleship(**{**base_pif_kwargs, "pifOptions": options})
    assert b.pifOptions["Board"][5][5] == "B"


def test_handle_entry_miss(battleship: Battleship) -> None:
    comment = Mock()
    comment.id = "c1"
    comment.created_utc = 2000000
    user = Mock()
    user.name = "p1"
    battleship.pifWinner = "TBD"
    with patch("random.choice", return_value="Aye aye!"):
        battleship.handle_entry(comment, user, ["latherbot", "in", "A", "5"])
    assert battleship.pifEntries["p1"]["GuessCol"] == "A"  # type: ignore[index]
    assert battleship.pifEntries["p1"]["GuessRow"] == 5  # type: ignore[index]


def test_handle_entry_hit(battleship: Battleship) -> None:
    comment = Mock()
    comment.id = "c1"
    comment.created_utc = 2000000
    user = Mock()
    user.name = "p1"
    battleship.pifWinner = "TBD"
    ship_row = battleship.pifOptions["StartRow"]
    ship_col = battleship.pifOptions["StartCol"]
    col_letter = chr(ord("A") + ship_col)
    with patch("random.choice", return_value="Aye aye!"):
        battleship.handle_entry(
            comment, user, ["latherbot", "in", col_letter, str(ship_row + 1)]
        )
    assert battleship.pifWinner == "p1"


def test_handle_entry_invalid_coordinates(battleship: Battleship) -> None:
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    battleship.handle_entry(comment, user, ["latherbot", "in", "ZZ"])
    comment.reply.assert_called_once()
    assert "try again" in comment.reply.call_args[0][0].lower()


def test_user_already_guessed(battleship: Battleship) -> None:
    battleship.pifEntries = {
        "p1": {"GuessCol": "A", "GuessRow": 5},
    }
    assert battleship.userAlreadyGuessed("A", 5) == "p1"
    assert battleship.userAlreadyGuessed("B", 5) is None


def test_calc_distance(battleship: Battleship) -> None:
    battleship.pifOptions["NorthSouth"] = 1
    battleship.pifOptions["StartRow"] = 0
    battleship.pifOptions["StartCol"] = 0
    dist = battleship.calc_distance(0, 0)
    assert dist == 0.0


def test_print_board(battleship: Battleship) -> None:
    board_str = battleship.print_board()
    assert "B" in board_str or "." in board_str
    assert len(board_str) > 100


def test_is_already_entered_true(battleship: Battleship) -> None:
    battleship.pifEntries = {"p1": {"GuessCol": "A", "GuessRow": 5}}
    user = Mock()
    user.name = "p1"
    comment = Mock()
    assert battleship.is_already_entered(user, comment)
