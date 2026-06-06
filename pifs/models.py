from typing import Any, TypedDict

from pydantic import BaseModel, Field


class PifStorageDict(TypedDict):
    SubmissionId: str
    Author: str
    PifType: str
    MinKarma: int
    PifOptions: dict[str, Any]
    PifEntries: dict[str, Any]
    KarmaFail: dict[str, Any]
    PifState: str
    PifWinner: str
    ExpireTime: int


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
