#!/usr/bin/env python3
#
#   File = pif_builder.py
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
from __future__ import annotations

import logging
import time
from typing import Any, TypeVar

from config import bot_name
from pifs.base_pif import BasePIF
from pifs.models import PifData, PifStorageDict
from pifs.registry import PIF_REGISTRY, known_pif_types, register_pif  # noqa: F401

T = TypeVar("T", bound="BasePIF")

# Import all PIF subclasses so their @register_pif decorators execute
from pifs.battleship_pif import Battleship  # noqa: E402, F401
from pifs.geo_pif import Geo  # noqa: E402, F401
from pifs.holdem_poker_pif import HoldemPoker  # noqa: E402, F401
from pifs.infinite_poker_pif import InfinitePoker  # noqa: E402, F401
from pifs.karma_only_pif import KarmaOnly  # noqa: E402, F401
from pifs.lottery_pif import Lottery  # noqa: E402, F401
from pifs.poker_pif import Poker  # noqa: E402, F401
from pifs.randomizer_pif import Randomizer  # noqa: E402, F401
from pifs.range_pif import Range  # noqa: E402, F401


def build_and_init_pif(submission: Any) -> Any | None:
    logging.info(
        'Scanning submission "%s" for a %s command', submission.title, bot_name
    )
    lines = submission.selftext.lower().split("\n")
    for line in lines:
        if line.strip().startswith(bot_name.lower()):
            pif = build_from_post(submission, line)
            if pif is None:
                continue
            else:
                logging.info('Initializing PIF "%s"', submission.title)
                pif.initialize()
                return pif
            break
    logging.warning(
        'No %s command found in submission "%s"', bot_name, submission.title
    )
    return None


def build_from_post(submission: Any, line: str) -> Any | None:
    logging.info(
        'Building PIF from command [%s] for submission "%s"', line, submission.title
    )
    try:
        parts = line.split()
        pif_type = parts[1]
        if pif_type not in PIF_REGISTRY:
            return None
        min_karma = parts[2]
        duration_hours = parts[3]
        end_time = int(submission.created_utc) + 3600 * int(duration_hours)

        if end_time < time.time():
            logging.info('PIF "%s" should already be closed', submission.title)
            submission.mod.flair(text="PIF - Closed", css_class="orange")
            submission.mod.lock()
            return None

        pif_cls = PIF_REGISTRY[pif_type]
        pif_options: dict[str, Any] = {}
        if pif_type == "range":
            range_min = int(parts[4])
            range_max = int(parts[5])
            if range_max <= range_min:
                submission.reply("I think you got your min and max mixed up")
                return None
            pif_options["RangeMin"] = range_min
            pif_options["RangeMax"] = range_max

        pif = pif_cls(
            submission.id,
            submission.author.name,
            min_karma,
            duration_hours,
            end_time,
            pifOptions=pif_options,
            pifEntries={},
            karmaFail={},
        )
        return pif
    except IndexError:
        logging.error("Not enough PIF parameters in input: [%s]", line)
        submission.reply(
            f"""Well this is embarassing.
        You said *{line}* and I couldn't figure out how to handle it.
        Maybe check the %s documentation and try again."""
            % bot_name
        )
    return None


def build_from_storage_dict(storage_dict: PifStorageDict) -> BasePIF | None:
    logging.debug("Building PIF object from %s", storage_dict)
    data = PifData.model_validate(storage_dict)
    pif_type = data.pif_type

    if pif_type not in PIF_REGISTRY:
        logging.error("Unsupported PIF type [%s]", pif_type)
        return None

    pif_cls = PIF_REGISTRY[pif_type]
    return pif_cls(  # type: ignore[no-any-return]
        data.post_id,
        data.author_name,
        str(data.min_karma),
        0,
        str(data.expire_time),
        data.pif_options,
        data.pif_entries,
        data.karma_fail,
    )
