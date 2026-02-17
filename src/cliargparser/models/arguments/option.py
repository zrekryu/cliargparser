from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import KW_ONLY, dataclass
from typing import Any

from cliargparser.actions import (
    append_present_action,
    count_presence_action,
    store_false_action,
    store_present_action,
    store_true_action,
    store_value_action,
)
from cliargparser.enums import NArgs
from cliargparser.hints import Action


@dataclass(frozen=True, slots=True)
class Option:
    long_names: tuple[str, ...]
    short_names: tuple[str, ...]

    _ = KW_ONLY

    aliases: tuple[str, ...]

    store_name: str

    action: Action[Option]
    nargs: int | NArgs

    default: Any
    present: Any

    type_converter: Callable[[str], Any]
    choices: tuple[Any, ...]
    required: bool

    @property
    def all_names(self) -> tuple[str, ...]:
        return self.short_names + self.long_names + self.aliases

    @property
    def takes_arguments(self) -> bool:
        if isinstance(self.nargs, int):
            return self.nargs > 0

        return True

    @classmethod
    def create(
        cls,
        long_names: str | Sequence[str] | None = None,
        short_names: str | Sequence[str] | None = None,
        *,
        aliases: str | Sequence[str] | None = None,
        store_name: str | None = None,
        action: Action[Option] | None = None,
        nargs: int | NArgs | None = None,
        present: Any | None = None,
        default: Any | None = None,
        type_converter: Callable[[str], Any] | None = None,
        choices: Sequence[Any] | None = None,
        required: bool = False,
    ) -> Option:
        long_names = (
            (long_names,) if isinstance(long_names, str) else tuple(long_names or ())
        )
        short_names = (
            (short_names,) if isinstance(short_names, str) else tuple(short_names or ())
        )
        aliases = (
            (aliases,) if isinstance(aliases, str) else tuple(aliases or ())
        )

        if not short_names and not long_names:
            raise ValueError(
                "Either short_names or long_names must be a non-empty sequence "
                f"(got: {short_names=}; {long_names=})"
            )

        for short_name in short_names:
            if len(short_name) > 1:
                raise ValueError("short name length must be 1")

        if store_name is None:
            store_name = long_names[0] if long_names else short_names[0]

        if action is None:
            action = store_value_action

        if nargs is None:
            if action in (
                store_present_action,
                store_true_action,
                store_false_action,
                append_present_action,
                count_presence_action,
            ):
                nargs = 0
            else:
                nargs = 1

        if action is append_present_action and present is None:
            raise ValueError(
                f"Missing 'present' value for action: "
                f"{getattr(action, "__name__", type(action).__name__)!r}"
            )

        return cls(
            long_names=long_names,
            short_names=short_names,
            aliases=aliases,
            store_name=store_name,
            action=action,
            nargs=nargs,
            present=present,
            default=default,
            type_converter=type_converter or str,
            choices=tuple(choices or ()),
            required=required
        )
