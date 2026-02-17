from ..parser import ParserError


class UnknownCommandError(ParserError):
    def __init__(self, name: str) -> None:
        self.name = name

        super().__init__(self.name)

    def __str__(self) -> str:
        return f"Unknown command: {self.name}"
