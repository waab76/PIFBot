from __future__ import annotations

from typing import Any, TypeVar

from pifs.base_pif import BasePIF

T = TypeVar("T", bound="BasePIF")

PIF_REGISTRY: dict[str, type[Any]] = {}


def register_pif(cls: type[T]) -> type[T]:
    PIF_REGISTRY[cls.pif_type] = cls
    return cls


def known_pif_types() -> list[str]:
    return list(PIF_REGISTRY.keys())
