#!/usr/bin/env python3
#
#   File = base_pif.py
#
#      Copyright 2020 Rob Curtis
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
############################################################################
import logging
from abc import ABC, abstractmethod
from typing import Any

from config import blacklist, bot_name
from pifs.karma_checker import check_karma
from pifs.models import EntryDict, OptionsDict, PifStorageDict
from utils.personality import get_bad_command_response
from utils.reddit_helper import get_submission


class BasePIF(ABC):
    pif_type: str = ""  # overridden by subclasses

    def __init__(
        self,
        postId: str,
        authorName: str,
        pifType: str,
        minKarma: int | str,
        durationHours: int | str,
        endTime: int | str,
        pifOptions: OptionsDict | None = None,
        pifEntries: dict[str, EntryDict | str] | None = None,
        karmaFail: dict[str, str] | None = None,
    ):
        logging.debug("Building PIF [%s]", postId)
        self.postId = postId
        self.authorName = authorName
        self.pifType = pifType
        self.minKarma = int(minKarma)
        self.durationHours = int(durationHours)
        self.pifOptions: OptionsDict = pifOptions or {}
        self.pifEntries: dict[str, EntryDict | str] = pifEntries or {}
        self.karmaFail: dict[str, str] = karmaFail or {}
        self.expireTime = int(endTime)
        self.pifState = "open"
        self.pifWinner = "TBD"

    def initialize(self) -> None:
        logging.debug("Adding PIF instructions")
        submission = get_submission(self.postId)
        comment = submission.reply(self.pif_instructions())
        comment.mod.distinguish("yes", True)

    def handle_comment(self, comment: Any) -> bool | None:
        # Look for a LatherBot command
        for line in comment.body.lower().split("\n"):
            if line.strip().startswith(bot_name.lower()):
                parts = line.split()
                if len(parts) < 2:
                    continue
                logging.info(
                    'Handling command [%s] for PIF "%s" by %s',
                    line,
                    comment.submission.title,
                    comment.author.name,
                )
                user = comment.author
                karma_result = check_karma(user, self.minKarma, self.postId)

                if karma_result.reason == "calculation_error":
                    comment.reply(
                        f"I cannot seem to calculate karma for user u/{user.name}"
                    )
                    comment.save()
                    return False

                if parts[1].startswith("in"):
                    if self.is_already_entered(user, comment):
                        logging.info(
                            'User %s is already entered in PIF "%s"',
                            user.name,
                            comment.submission.title,
                        )
                        comment.reply(
                            f"User {user.name} is already entered in this PIF"
                        )
                        comment.save()
                    elif karma_result.reason == "blacklisted":
                        logging.info(
                            "User %s is on the PIF blacklist [%s]",
                            user.name,
                            blacklist[user.name],
                        )
                        user.message(
                            "PIF Entry Denied",
                            f"Your attempt to enter PIF http://redd.it/{self.postId}"
                            f" has been denied.\n\n{blacklist[user.name]}",
                        )
                        comment.save()
                    elif user.name in self.karmaFail:
                        comment.reply(
                            f"u/{user.name} has already failed the karma check "
                            f"for this PIF",
                        )
                        comment.save()
                    elif user.name == self.authorName:
                        logging.info(
                            "User %s has tried to enter their own PIF", user.name
                        )
                        comment.reply(
                            "Are you kidding me? This is your PIF.  If you want "
                            "it that much, just keep it.",
                        )
                        comment.save()
                    elif user.created_utc > comment.submission.created_utc:
                        logging.warning(
                            "User %s appears to be a sock puppet", user.name
                        )
                        comment.reply(
                            f"Account u/{user.name} appears to be a sock puppet "
                            f"account created just to enter this PIF. Entry denied.",
                        )
                        comment.save()
                    elif karma_result.passed:
                        logging.debug(
                            "User %s meets karma requirement for PIF [%s]",
                            user.name,
                            self.postId,
                        )
                        self.handle_entry(comment, user, parts)
                        return True
                    else:
                        assert karma_result.karma is not None
                        assert karma_result.formatted_karma is not None
                        logging.info(
                            'User %s does not have enough karma for PIF "%s"',
                            user.name,
                            comment.submission.title,
                        )
                        karma_fail: dict[str, Any] = {}
                        karma_fail["CommentId"] = comment.id
                        karma_fail["Karma"] = karma_result.karma[0]
                        self.karmaFail[user.name] = karma_fail  # type: ignore[assignment]
                        comment.reply(
                            "I'm afraid you don't have the karma for this PIF\n\n"
                            + karma_result.formatted_karma
                            + (
                                "\n\nThe PIF author can override the karma check by "
                                "responding to this comment with the command "
                                f"`{bot_name} override`"
                            )
                        )
                        comment.save()
                        return True
                elif parts[1].startswith("karma"):
                    logging.info("User %s requested karma check", user.name)
                    if karma_result.formatted_karma:
                        comment.reply(karma_result.formatted_karma)
                    else:
                        comment.reply("Unable to calculate karma")
                    comment.downvote()
                    comment.save()
                elif parts[1].startswith("override"):
                    logging.info("User %s requested karma override", user.name)
                    self.karma_override(comment)
                    comment.save()
                    return True
                else:
                    logging.warning(
                        'Invalid command on comment [%s] for post "%s" by user %s',
                        comment.id,
                        comment.submission.title,
                        comment.author.name,
                    )
                    comment.reply(
                        f"That was not a valid `{bot_name}` command.  "
                        f"Whatever you were trying to do, you'll need to "
                        f"try again in a brand new comment."
                        f"\n\n{get_bad_command_response()}"
                    )
                    comment.save()

                return False

        return None

    def to_storage_dict(self) -> PifStorageDict:
        return {
            "SubmissionId": self.postId,
            "Author": self.authorName,
            "PifType": self.pifType,
            "MinKarma": self.minKarma,
            "DurationHours": self.durationHours,
            "PifOptions": self.pifOptions,
            "PifEntries": self.pifEntries,
            "KarmaFail": self.karmaFail,
            "PifState": self.pifState,
            "PifWinner": self.pifWinner,
            "ExpireTime": self.expireTime,
        }

    def finalize(self) -> None:
        logging.info("Finalizing PIF [%s]", self.postId)
        # Get the original PIF post
        submission = get_submission(self.postId)

        comment = None
        if len(self.pifEntries) < 1:
            logging.warning("PIF [%s] did not receive any entries", self.postId)
            comment = submission.reply(
                "There were no qualified entries. The PIF is a bust."
            )
            try:
                submission.mod.flair(
                    flair_template_id="ddc27296-0d64-11e8-a87d-0e644179e478"
                )
            except Exception:
                logging.warning(
                    "Primary flair template failed for PIF [%s], trying fallback",
                    self.postId,
                    exc_info=True,
                )
                try:
                    submission.mod.flair(
                        flair_template_id="600e182a-fb07-11eb-949a-3234ae962371"
                    )
                except Exception:
                    logging.error(
                        "Fallback flair template also failed for PIF [%s]",
                        self.postId,
                        exc_info=True,
                    )
        else:
            self.determine_winner()
            comment = submission.reply(self.generate_winner_comment())
            try:
                submission.mod.flair(
                    flair_template_id="e05501c2-0d64-11e8-80c6-0e2446bb425c"
                )
            except Exception:
                logging.warning(
                    "Primary winner flair template failed for PIF [%s], "
                    "trying fallback",
                    self.postId,
                    exc_info=True,
                )
                try:
                    submission.mod.flair(
                        flair_template_id="600e182a-fb07-11eb-949a-3234ae962371"
                    )
                except Exception:
                    logging.error(
                        "Fallback flair template also failed for PIF [%s]",
                        self.postId,
                        exc_info=True,
                    )

        logging.info("Closing PIF [%s]", self.postId)
        comment.mod.distinguish("yes", True)
        # submission.mod.lock()
        self.pifState = "closed"

    def karma_override(self, comment: Any) -> None:
        if comment.author.name == self.authorName:
            logging.debug("Passed PIF author check")
            parent_comment = comment.parent()
            if parent_comment.author.name == bot_name:
                logging.debug('Passed "responding to %s" check', bot_name)
                grandparent_comment = parent_comment.parent()
                lucky_stiff = grandparent_comment.author
                if lucky_stiff is None:
                    comment.reply("Sorry, looks like the comment is gone")
                elif lucky_stiff.name in self.karmaFail:
                    logging.debug("User %s did fail the karma check", lucky_stiff.name)
                    self.karmaFail.pop(lucky_stiff.name)
                    for line in grandparent_comment.body.lower().split("\n"):
                        if line.strip().startswith(bot_name.lower()):
                            parts = line.split()
                            if len(parts) < 2:
                                continue
                            logging.info(
                                "Reprocessing command [%s] from user %s",
                                " ".join(parts),
                                lucky_stiff.name,
                            )
                            self.handle_entry(grandparent_comment, lucky_stiff, parts)
                            break
                else:
                    comment.reply(
                        f"I am confused. u/{lucky_stiff} did not fail the karma check"
                    )
            else:
                comment.reply("I am not sure what you are trying to do.")
        else:
            logging.error(
                "Attempted karma override by %s, who is not the PIF author",
                comment.author.name,
            )
            comment.reply(
                "This is not your PIF and you cannot override the karma check."
            )

    def is_already_entered(self, user: Any, comment: Any) -> bool:
        if user.name in self.pifEntries:
            logging.info(
                "User %s appears to have already entered PIF [%s] with comment [%s]",
                user.name,
                self.postId,
                self.pifEntries[user.name]["CommentId"],  # type: ignore[index]
            )
            return True
        else:
            return False

    @abstractmethod
    def pif_instructions(self) -> str: ...

    @abstractmethod
    def handle_entry(
        self, comment: Any, user: Any, command_parts: list[str]
    ) -> None: ...

    @abstractmethod
    def determine_winner(self) -> None: ...

    @abstractmethod
    def generate_winner_comment(self) -> str: ...
