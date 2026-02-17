from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol


if TYPE_CHECKING:
    from .models.arguments import Command, Operand, Option


class Action[
    P: (Option, Command, Operand)
](Protocol):
    def __call__(
        self,
        argument: P,
        values: Sequence[Any],
        current_value: Any = None
    ) -> Any: ...
