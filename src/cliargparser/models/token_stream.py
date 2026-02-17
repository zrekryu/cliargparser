from __future__ import annotations

from collections.abc import Iterable


class TokenStream:
    __slots__ = ("_buffer", "_iter")

    def __init__(self, iterable: Iterable[str]) -> None:
        self._iter = iter(iterable)

        self._buffer: str | None = None

    def peek(self) -> str | None:
        if self._buffer is None:
            try:
                self._buffer = next(self._iter)
            except StopIteration:
                return None

        return self._buffer

    def consume(self) -> str | None:
        token = self.peek()
        self._buffer = None
        return token

    def __iter__(self) -> TokenStream:
        return self

    def __next__(self) -> str:
        token = self.peek()
        if token is None:
            raise StopIteration

        self._buffer = None

        return token
