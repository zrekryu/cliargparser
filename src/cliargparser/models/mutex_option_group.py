from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from ..enums import NArgs
from ..hints import Action
from .arguments.option import Option


@dataclass(frozen=True, slots=True)
class MutexOptionGroup:
    required: bool = False

    _options: list[Option] = field(default_factory=list[Option], init=False)

    @property
    def options(self) -> tuple[Option, ...]:
        return tuple(self._options)

    def add_option(self, option: Option) -> None:
        self._options.append(option)

    def option(
        self,
        long_names: str | Sequence[str] | None = None,
        short_names: str | Sequence[str] | None = None,
        aliases: str | Sequence[str] | None = None,
        store_name: str | None = None,
        action: Action[Option] | None = None,
        nargs: int | NArgs | None = None,
        present: Any | None = None,
        default: Any | None = None,
        type_converter: Callable[[str], Any] | None = None,
        choices: Sequence[Any] | None = None
    ) -> Option:
        option = Option.create(
            long_names=long_names,
            short_names=short_names,
            aliases=aliases,
            store_name=store_name,
            action=action,
            nargs=nargs,
            present=present,
            default=default,
            type_converter=type_converter,
            choices=choices
        )
        self._options.append(option)

        return option
