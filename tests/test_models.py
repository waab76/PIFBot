from __future__ import annotations

import pytest
from pydantic import ValidationError

from pifs.models import EntryDict, OptionsDict, PifData, PifStorageDict


class TestPifData:
    def test_model_validate_full_dict(self) -> None:
        data: PifStorageDict = {
            "SubmissionId": "post_1",
            "Author": "user1",
            "PifType": "lottery",
            "MinKarma": 50,
            "DurationHours": 24,
            "ExpireTime": 9999999999,
            "PifState": "open",
            "PifWinner": "TBD",
            "PifOptions": {},
            "PifEntries": {"player1": "comment_1"},
            "KarmaFail": {},
        }
        pif = PifData.model_validate(data)
        assert pif.post_id == "post_1"
        assert pif.author_name == "user1"
        assert pif.pif_type == "lottery"
        assert pif.min_karma == 50
        assert pif.pif_state == "open"

    def test_model_validate_minimal_dict(self) -> None:
        data: PifStorageDict = {
            "SubmissionId": "post_2",
            "Author": "user2",
            "PifType": "range",
            "MinKarma": 25,
            "DurationHours": 48,
            "ExpireTime": 8888888888,
            "PifState": "open",
            "PifWinner": "TBD",
            "PifOptions": {"RangeMin": 1, "RangeMax": 100},
            "PifEntries": {},
            "KarmaFail": {},
        }
        pif = PifData.model_validate(data)
        assert pif.pif_options == {"RangeMin": 1, "RangeMax": 100}
        assert pif.pif_entries == {}

    def test_model_validate_missing_state_uses_default(self) -> None:
        data: PifStorageDict = {
            "SubmissionId": "post_3",
            "Author": "user3",
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
        pif = PifData.model_validate(data)
        assert pif.pif_state == "open"

    def test_model_validate_missing_required_raises(self) -> None:
        with pytest.raises(ValidationError):
            PifData.model_validate({})

    def test_serialization_round_trip(self) -> None:
        data: PifStorageDict = {
            "SubmissionId": "post_1",
            "Author": "user1",
            "PifType": "lottery",
            "MinKarma": 50,
            "DurationHours": 24,
            "ExpireTime": 9999999999,
            "PifState": "open",
            "PifWinner": "TBD",
            "PifOptions": {"Deck": []},
            "PifEntries": {"player1": "comment_1"},
            "KarmaFail": {},
        }
        pif = PifData.model_validate(data)
        serialized = pif.model_dump(by_alias=True)
        assert serialized["SubmissionId"] == "post_1"
        assert serialized["PifType"] == "lottery"
        assert serialized["PifOptions"] == {"Deck": []}

    def test_model_validate_pif_entries_with_entry_dict(self) -> None:
        entry: EntryDict = {
            "CommentId": "comm_1",
            "Guess": 42,
        }
        data: PifStorageDict = {
            "SubmissionId": "post_r",
            "Author": "author",
            "PifType": "range",
            "MinKarma": 10,
            "DurationHours": 24,
            "ExpireTime": 9999999999,
            "PifState": "open",
            "PifWinner": "TBD",
            "PifOptions": {},
            "PifEntries": {"player1": entry},
            "KarmaFail": {},
        }
        pif = PifData.model_validate(data)
        assert pif.pif_entries["player1"]["CommentId"] == "comm_1"
