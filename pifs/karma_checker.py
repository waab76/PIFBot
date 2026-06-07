from __future__ import annotations

import logging
from typing import Any

import config
from utils.karma_calculator import calculate_karma, formatted_karma


class KarmaCheckResult:
    """Result of a karma check for a user."""

    def __init__(
        self,
        passed: bool,
        user: Any,
        reason: str = "",
        karma: tuple[int, int, int, int, int] | None = None,
        formatted_karma: str | None = None,
    ):
        self.passed = passed
        self.user = user
        self.reason = reason  # "blacklisted", "karma_failed", "calculation_error", ""
        self.karma = karma
        self.formatted_karma = formatted_karma


def check_karma(user: Any, min_karma: int, pif_id: str) -> KarmaCheckResult:
    """Check if a user meets the minimum karma requirement.

    Args:
        user: PRAW Redditor object.
        min_karma: Minimum karma required.
        pif_id: PIF post ID for logging.

    Returns:
        KarmaCheckResult with pass/fail status, reason, and karma details.
    """
    if user.name in config.blacklist:
        logging.info(
            "User %s is on the PIF blacklist [%s]",
            user.name,
            pif_id,
        )
        return KarmaCheckResult(
            passed=False,
            user=user,
            reason="blacklisted",
        )

    karma = calculate_karma(user)
    if not karma:
        logging.error(
            "Failed to calculate karma for user %s [%s]",
            user.name,
            pif_id,
        )
        return KarmaCheckResult(
            passed=False,
            user=user,
            reason="calculation_error",
        )

    passed = karma[0] >= min_karma
    formatted = formatted_karma(user, karma)

    return KarmaCheckResult(
        passed=passed,
        user=user,
        reason="" if passed else "karma_failed",
        karma=karma,
        formatted_karma=formatted,
    )
