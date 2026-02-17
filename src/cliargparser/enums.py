from enum import StrEnum


class ParseMode(StrEnum):
    COMMAND = "command"
    OPERAND = "operand"


class ParsingSentinel(StrEnum):
    END_OF_OPTIONS = "--"


class OptionPrefix(StrEnum):
    SHORT = "-"
    LONG = "--"


class OptionToken(StrEnum):
    EXPLICIT_ARGUMENT = "="


class NArgs(StrEnum):
    OPTIONAL = "?"

    ZERO_OR_MORE = "*"
    ONE_OR_MORE = "+"
