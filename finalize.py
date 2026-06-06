"""
Created on Feb 13, 2021

@author: rcurtis
"""

from __future__ import annotations

import sys

from pifs.base_pif import BasePIF
from utils.pif_storage import get_pif


def finalize(pif_id: str) -> None:
    pif: BasePIF | None = get_pif(pif_id)
    if pif is not None:
        pif.finalize()


if __name__ == "__main__":
    finalize(sys.argv[1])
