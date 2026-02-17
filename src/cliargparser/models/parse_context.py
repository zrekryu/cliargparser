from dataclasses import dataclass

from .arguments.command import Command
from .namespace import Namespace
from .token_stream import TokenStream


@dataclass(slots=True)
class ParseContext:
    command: Command
    namespace: Namespace
    token_stream: TokenStream
    end_of_options: bool = False
    operand_index: int = 0