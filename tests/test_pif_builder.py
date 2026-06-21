from __future__ import annotations

from unittest.mock import Mock

from config import bot_name
from pifs import pif_builder
from pifs.base_pif import BasePIF
from pifs.models import PifStorageDict
from pifs.registry import PIF_REGISTRY, known_pif_types


def test_register_pif_adds_to_registry() -> None:
    assert "lottery" in PIF_REGISTRY
    assert "range" in PIF_REGISTRY
    assert "geo" in PIF_REGISTRY
    assert "battleship" in PIF_REGISTRY
    assert "poker" in PIF_REGISTRY
    assert "infinite-poker" in PIF_REGISTRY
    assert "holdem-poker" in PIF_REGISTRY
    assert "randomizer" in PIF_REGISTRY
    assert "karma-only" in PIF_REGISTRY


def test_known_pif_types_returns_all() -> None:
    types = known_pif_types()
    assert "lottery" in types
    assert "range" in types
    assert len(types) >= 9


def test_build_from_storage_dict_lottery() -> None:
    data: PifStorageDict = {
        "SubmissionId": "post_1",
        "Author": "author",
        "PifType": "lottery",
        "MinKarma": 50,
        "DurationHours": 24,
        "ExpireTime": 9999999999,
        "PifState": "open",
        "PifWinner": "TBD",
        "PifOptions": {},
        "PifEntries": {},
        "KarmaFail": {},
    }
    pif = pif_builder.build_from_storage_dict(data)
    assert pif is not None
    assert pif.pifType == "lottery"
    assert pif.postId == "post_1"


def test_build_from_storage_dict_range() -> None:
    data: PifStorageDict = {
        "SubmissionId": "post_r",
        "Author": "author",
        "PifType": "range",
        "MinKarma": 10,
        "DurationHours": 48,
        "ExpireTime": 9999999999,
        "PifState": "open",
        "PifWinner": "TBD",
        "PifOptions": {"RangeMin": 1, "RangeMax": 100},
        "PifEntries": {},
        "KarmaFail": {},
    }
    pif = pif_builder.build_from_storage_dict(data)
    assert pif is not None
    assert isinstance(pif, BasePIF)
    assert pif.pifOptions["RangeMin"] == 1
    assert pif.pifOptions["RangeMax"] == 100


def test_build_from_storage_dict_unknown_type() -> None:
    data: PifStorageDict = {
        "SubmissionId": "post_x",
        "Author": "author",
        "PifType": "nonexistent",
        "MinKarma": 50,
        "DurationHours": 24,
        "ExpireTime": 9999999999,
        "PifState": "open",
        "PifWinner": "TBD",
        "PifOptions": {},
        "PifEntries": {},
        "KarmaFail": {},
    }
    pif = pif_builder.build_from_storage_dict(data)
    assert pif is None


def test_build_from_post_lottery() -> None:
    submission = Mock()
    submission.id = "post_1"
    submission.author.name = "author"
    submission.created_utc = 9999913599  # far future, won't be expired

    pif = pif_builder.build_from_post(submission, f"{bot_name.lower()} lottery 50 24")
    assert pif is not None
    assert pif.pifType == "lottery"
    assert pif.minKarma == 50
    assert pif.durationHours == 24


def test_build_from_post_range_with_min_max() -> None:
    submission = Mock()
    submission.id = "post_r"
    submission.author.name = "author"
    submission.created_utc = 9999913599  # far future, won't be expired

    pif = pif_builder.build_from_post(
        submission, f"{bot_name.lower()} range 10 48 1 100"
    )
    assert pif is not None
    assert pif.pifType == "range"
    assert pif.pifOptions["RangeMin"] == 1
    assert pif.pifOptions["RangeMax"] == 100


def test_build_from_post_range_inverted_min_max_returns_none() -> None:
    submission = Mock()
    submission.id = "post_r"
    submission.author.name = "author"
    submission.created_utc = 1500000

    pif = pif_builder.build_from_post(
        submission, f"{bot_name.lower()} range 10 48 100 1"
    )
    assert pif is None


def test_build_from_post_expired_pif_returns_none() -> None:
    submission = Mock()
    submission.id = "post_1"
    submission.author.name = "author"
    submission.created_utc = 1  # ancient — expired immediately

    pif = pif_builder.build_from_post(submission, f"{bot_name.lower()} lottery 50 24")
    assert pif is None


def test_build_from_post_unknown_type_returns_none() -> None:
    submission = Mock()
    submission.id = "post_x"
    submission.author.name = "author"
    submission.created_utc = 1500000

    pif = pif_builder.build_from_post(
        submission, f"{bot_name.lower()} unknown_type 50 24"
    )
    assert pif is None
