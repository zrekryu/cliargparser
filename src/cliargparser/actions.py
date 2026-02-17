from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal


if TYPE_CHECKING:
    from .models.arguments import Operand, Option


def store_value_action[T](
    argument: Option | Operand, values: Sequence[T], current_value: Any = None
) -> T | None:
    return values[0] if values else None


def store_present_action(
    argument: Option, values: Sequence[Any], current_value: Any = None
) -> Any:
    return argument.present


def store_true_action(
    argument: Option, values: Sequence[Any], current_value: bool | None = None
) -> Literal[True]:
    return True


def store_false_action(
    argument: Option, values: Sequence[Any], current_value: bool | None = None
) -> Literal[False]:
    return False


def append_present_action(
    argument: Option, values: Sequence[Any], current_value: list[Any] | None = None
) -> list[Any]:
    if current_value is None:
        current_value = []

    current_value.append(argument.present)
    return current_value


def append_value_action(
    argument: Option | Operand,
    values: Sequence[Any],
    current_value: list[Any] | None = None
) -> list[Any]:
    if current_value is None:
        current_value = []

    if values:
        current_value.append(values)

    return current_value


def extend_value_action(
    argument: Option | Operand,
    values: Sequence[Any],
    current_value: list[Any] | None = None
) -> list[Any]:
    if current_value is None:
        current_value = []

    current_value.extend(values)
    return current_value


def count_presence_action(
    argument: Option, values: Sequence[Any], current_value: int | None = None
) -> int:
    if current_value is None:
        return 1

    return current_value + 1
