from typing import Any, TypedDict

from pydantic import BaseModel, Field


class EntryDict(TypedDict, total=False):
    """Base entry dict — each PIF type stores different fields.

    Common fields:
    - CommentId: str — the Reddit comment ID for the entry

    PIF-specific fields:
    - Range: Guess (int)
    - Geo: Guess (str), GuessAddr (str), GuessLatLon (str)
    - Battleship: GuessTime (int), GuessCol (str), GuessRow (int)
    - Poker: UserCards (list), UserHand (list), HandScore (int)
    - InfinitePoker: UserHand (list), HandScore (int)
    - HoldemPoker: UserHoleCards (list), BestHand (list), HandScore (int)
    - Lottery/Randomizer: no additional fields (value is just comment ID)
    """
    CommentId: str
    Guess: int
    GuessAddr: str
    GuessLatLon: str
    GuessTime: int
    GuessCol: str
    GuessRow: int
    UserCards: list[Any]
    UserHand: list[Any]
    HandScore: int
    UserHoleCards: list[Any]
    BestHand: list[Any]


class OptionsDict(TypedDict, total=False):
    """PIF options dict — each PIF type stores different configuration.

    PIF-specific fields:
    - Range: RangeMin (int), RangeMax (int)
    - Poker: Deck (list), SharedCards (list)
    - InfinitePoker: no options
    - HoldemPoker: FlopCards (list), RiverCard (list), TurnCard (list), ExtraInfo (str), hands (str JSON)
    - Geo: WinLatLon (str)
    - Battleship: Board (list[list[str]]), NorthSouth (int), StartRow (int), StartCol (int)
    - Lottery/Randomizer/KarmaOnly: no options
    """
    RangeMin: int
    RangeMax: int
    Deck: list[Any]
    SharedCards: list[Any]
    FlopCards: list[Any]
    RiverCard: list[Any]
    TurnCard: list[Any]
    ExtraInfo: str
    hands: str
    WinLatLon: str
    Board: list[list[str]]
    NorthSouth: int
    StartRow: int
    StartCol: int


class PifStorageDict(TypedDict):
    SubmissionId: str
    Author: str
    PifType: str
    MinKarma: int
    DurationHours: int
    ExpireTime: int
    PifState: str
    PifWinner: Any  # str or list[str] for Randomizer
    PifOptions: OptionsDict
    PifEntries: dict[str, EntryDict | str]
    KarmaFail: dict[str, str]


class PifData(BaseModel):
    post_id: str = Field(alias="SubmissionId")
    author_name: str = Field(alias="Author")
    pif_type: str = Field(alias="PifType")
    min_karma: int = Field(alias="MinKarma")
    expire_time: int = Field(alias="ExpireTime")
    pif_options: dict[str, Any] = Field(default_factory=dict, alias="PifOptions")
    pif_entries: dict[str, Any] = Field(default_factory=dict, alias="PifEntries")
    karma_fail: dict[str, Any] = Field(default_factory=dict, alias="KarmaFail")
    pif_state: str = Field(default="open", alias="PifState")
    pif_winner: str = Field(default="TBD", alias="PifWinner")
