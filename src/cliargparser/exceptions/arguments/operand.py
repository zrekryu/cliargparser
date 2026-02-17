from typing import TYPE_CHECKING

from cliargparser.enums import NArgs

from ..parser import ParserError
from .argument import MissingArgumentsError


if TYPE_CHECKING:
    from cliargparser.models.arguments import Operand


class OperandAfterNonDeterministicOperandError(ParserError):
    def __init__(self, operand: Operand) -> None:
        self.operand = operand

        super().__init__(self.operand)

    def __str__(self) -> str:
        return (
            f"Cannot add operands "
            f"after a non-deterministic operand: {self.operand.name}"
        )


class MissingOperandArgumentsError(MissingArgumentsError):
    def __init__(self, name: str, nargs: int | NArgs, received_nargs: int) -> None:
        self.name = name
        self.nargs = nargs
        self.received_nargs = received_nargs

        super().__init__(self.name, self.nargs, self.received_nargs)

    def __str__(self) -> str:
        s = "s" if isinstance(self.nargs, int) and self.nargs != 1 else ""
        return (
            f"Operand {self.name!r} expected {self.nargs} argument{s}, "
            f"got {self.received_nargs}"
        )


class ExtraOperandError(ParserError):
    def __init__(self, token: str) -> None:
        self.token = token

        super().__init__(self.token)

    def __str__(self) -> str:
        return f"Unexpected extra operand: {self.token}"