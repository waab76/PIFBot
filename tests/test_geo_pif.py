from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import pytest

from pifs.geo_pif import Geo


@pytest.fixture
def geo_pif(base_pif_kwargs: dict[str, Any]) -> Geo:
    return Geo(**base_pif_kwargs)


def test_handle_entry_valid_guess(geo_pif: Geo) -> None:
    comment = Mock()
    comment.id = "c1"
    comment.created_utc = 1000000
    user = Mock()
    user.name = "p1"
    mock_location = Mock()
    mock_location.address = "Cleveland, Ohio"
    mock_location.latitude = 41.5
    mock_location.longitude = -81.7
    with patch("pifs.geo_pif.geolocator.geocode", return_value=mock_location):
        geo_pif.handle_entry(comment, user, ["latherbot", "in", "Cleveland,", "Ohio"])
    entry = geo_pif.pifEntries["p1"]
    assert isinstance(entry, dict)
    assert "GuessAddr" in entry
    assert entry["GuessAddr"] == "Cleveland, Ohio"


def test_handle_entry_unfindable_location(geo_pif: Geo) -> None:
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    with patch("pifs.geo_pif.geolocator.geocode", return_value=None):
        geo_pif.handle_entry(comment, user, ["latherbot", "in", "Nowhere"])
    comment.reply.assert_called_once()
    assert "couldn't find" in comment.reply.call_args[0][0].lower()


def test_handle_entry_missing_guess(geo_pif: Geo) -> None:
    comment = Mock()
    comment.id = "c1"
    user = Mock()
    user.name = "p1"
    geo_pif.handle_entry(comment, user, ["latherbot", "in"])
    comment.reply.assert_called_once()
    assert "try again" in comment.reply.call_args[0][0].lower()


def test_user_already_guessed(geo_pif: Geo) -> None:
    geo_pif.pifEntries = {
        "p1": {"GuessAddr": "Cleveland, Ohio"},
    }
    assert geo_pif.userAlreadyGuessed("Cleveland, Ohio") == "p1"
    assert geo_pif.userAlreadyGuessed("New York") is None
