from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
import os
import sys
from typing import TYPE_CHECKING, Any

from cliargparser.enums import NArgs, ParseMode
from cliargparser.exceptions import (
    OperandAfterNonDeterministicOperandError,
    ParseModeError,
)
from cliargparser.hints import Action


if TYPE_CHECKING:
    from ..mutex_option_group import MutexOptionGroup

from ..namespace import Namespace
from .operand import Operand
from .option import Option


class Command:
    __slots__ = (
        "_mutex_option_groups",
        "_operands",
        "_options",
        "_subcommands",
        "aliases",
        "name",
        "non_deterministic_operand",
        "parse_mode",
        "subcommand_required"
    )

    def __init__(
        self,
        name: str | None = None,
        *,
        aliases: str | Sequence[str] | None = None,
        parse_mode: ParseMode | None = None,
        subcommand_required: bool = False,
    ) -> None:
        self.name = os.path.basename(sys.argv[0]) if name is None else name
        self.aliases: Sequence[str] = aliases or []
        self.parse_mode = parse_mode or ParseMode.COMMAND
        self.subcommand_required = subcommand_required

        self._options: list[Option] = []
        self._mutex_option_groups: list[MutexOptionGroup] = []

        self._subcommands: list[Command] = []
        self._operands: list[Operand] = []

        self.non_deterministic_operand: Operand | None = None

    @property
    def all_names(self) -> tuple[str, ...]:
        return (
            self.name,
            *((self.aliases,) if isinstance(self.aliases, str) else self.aliases)
        )

    @property
    def options(self) -> tuple[Option, ...]:
        return tuple(self._options)

    @property
    def mutex_option_groups(self) -> tuple[MutexOptionGroup, ...]:
        return tuple(self._mutex_option_groups)

    @property
    def subcommands(self) -> tuple[Command, ...]:
        return tuple(self._subcommands)

    @property
    def operands(self) -> tuple[Operand, ...]:
        return tuple(self._operands)

    def add_option(self, option: Option) -> None:
        self._options.append(option)

    def option(
        self,
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
            choices=choices,
            required=required
        )
        self._options.append(option)

        return option

    def get_option(self, name: str) -> Option | None:
        return next(
            (option for option in self.options if name in option.all_names),
            None
        )

    def add_mutex_option_group(self, mutex_option_group: MutexOptionGroup) -> None:
        self._mutex_option_groups.append(mutex_option_group)

    def add_subcommand(self, subcommand: Command) -> None:
        self._subcommands.append(subcommand)

    def subcommand(
        self,
        name: str,
        *,
        parse_mode: ParseMode | None = None,
        subcommand_required: bool = False
    ) -> Command:
        if self.parse_mode is not ParseMode.COMMAND:
            raise ParseModeError(
                f"Subcommands are not allowed in {self.parse_mode.name} parse mode"
            )

        subcommand = Command(
            name=name,
            parse_mode=parse_mode,
            subcommand_required=subcommand_required
        )
        self._subcommands.append(subcommand)

        return subcommand

    def get_subcommand(self, name: str) -> Command | None:
        return next(
            (
                subcommand for subcommand in self.subcommands
                if name in subcommand.all_names
            ),
            None
        )

    def add_operand(self, operand: Operand) -> None:
        self._operands.append(operand)

    def operand(
        self,
        name: str,
        *,
        action: Action[Operand] | None = None,
        nargs: int | NArgs | None = None,
        default: Any | None = None,
        type_converter: Callable[[str], Any] | None = None,
        choices: Sequence[Any] | None = None
    ) -> Operand:
        if self.parse_mode is not ParseMode.OPERAND:
            raise ParseModeError(
                f"Operands are not allowed in {self.parse_mode.name} parse mode"
            )

        if self.non_deterministic_operand:
            raise OperandAfterNonDeterministicOperandError(
                self.non_deterministic_operand
            )

        operand = Operand.create(
            name=name,
            action=action,
            nargs=nargs,
            default=default,
            type_converter=type_converter,
            choices=choices
        )
        self._operands.append(operand)

        if isinstance(operand.nargs, NArgs):
            self.non_deterministic_operand = operand

        return operand

    def get_operand(self, name: str) -> Operand | None:
        return next(
            (operand for operand in self.operands if name == operand.name),
            None
        )

    def get_operand_by_index(self, index: int) -> Operand:
        return self._operands[index]

    def parse_arguments(self, arguments: str | Iterable[str]) -> Namespace:
        from cliargparser import (
            ArgumentParser,  # Until only Python `3.15+` is supported.
        )

        return ArgumentParser.parse_arguments(arguments, self)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"options={self.options}, "
            f"subcommands={self.subcommands}, "
            f"operands={self.operands}, "
            f"non_deterministic_operand={self.non_deterministic_operand}"
            ")"
        )
