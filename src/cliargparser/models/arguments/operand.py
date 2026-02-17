from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import KW_ONLY, dataclass
from typing import Any

from cliargparser.actions import store_value_action
from cliargparser.enums import NArgs
from cliargparser.hints import Action


@dataclass(frozen=True, slots=True)
class Operand:
    name: str

    _ = KW_ONLY

    action: Action[Operand]
    nargs: int | NArgs

    default: Any

    type_converter: Callable[[str], Any]
    choices: tuple[Any, ...]

    @property
    def takes_arguments(self) -> bool:
        if isinstance(self.nargs, int):
            return self.nargs > 1
        elif self.nargs is NArgs.OPTIONAL:
            return False

        return True

    @classmethod
    def create(
        cls,
        name: str,
        *,
        action: Action[Operand] | None = None,
        nargs: int | NArgs | None = None,
        default: Any | None = None,
        type_converter: Callable[[str], Any] | None = None,
        choices: Sequence[Any] | None = None
    ) -> Operand:
        if action is None:
            action = store_value_action

        if nargs is None:
            nargs = 1

        if isinstance(nargs, int) and nargs == 0:
            raise ValueError("Operand's nargs cannot be zero")

        return cls(
            name=name,
            action=action,
            nargs=nargs,
            default=default,
            type_converter=type_converter or str,
            choices=tuple(choices or ())
        )