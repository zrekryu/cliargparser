from cliargparser.enums import NArgs, OptionPrefix

from ..parser import ParserError
from .argument import MissingArgumentsError


class UnknownOptionError(ParserError):
    pass


class UnknownLongOptionError(UnknownOptionError):
    def __init__(self, name: str) -> None:
        self.name = name

        super().__init__(self.name)

    def __str__(self) -> str:
        return f"Unknown long option: {OptionPrefix.LONG}{self.name}"


class UnknownShortOptionError(UnknownOptionError):
    def __init__(self, name: str) -> None:
        self.name = name

        super().__init__(self.name)

    def __str__(self) -> str:
        return f"Unknown short option: {OptionPrefix.SHORT}{self.name}"


class UnknownShortOptionInGroupError(UnknownOptionError):
    def __init__(self, name: str, group: str) -> None:
        self.name = name
        self.group = group

        super().__init__(self.name, self.group)

    def __str__(self) -> str:
        return (
            f"Unknown short option {self.name!r} "
            f"in group {self.group!r}"
        )


class OptionTakesNoArgumentError(ParserError):
    def __init__(self, token: str, value: str) -> None:
        self.token = token
        self.value = value

        super().__init__(self.token, self.value)

    def __str__(self) -> str:
        return (
            f"Option {self.token!r} takes no arguments, "
            f"got an explicit argument: {self.value}"
        )


class MissingOptionArgumentsError(MissingArgumentsError):
    def __init__(self, token: str, nargs: int | NArgs, received_nargs: int) -> None:
        self.token = token
        self.nargs = nargs
        self.received_nargs = received_nargs

        super().__init__(self.token, self.nargs, self.received_nargs)

    def __str__(self) -> str:
        s = "s" if isinstance(self.nargs, int) and self.nargs != 1 else ""
        return (
            f"Option {self.token!r} expected {self.nargs} argument{s}, "
            f"got {self.received_nargs}"
        )


class OptionInGroupTakesArgumentsError(ParserError):
    def __init__(self, name: str, group: str) -> None:
        self.name = name
        self.group = group

        super().__init__(self.name, self.group)

    def __str__(self) -> str:
        return (
            f"Argument-taking option {self.name!r} "
            f"is not allowed in short option group {self.group!r}"
        )
        