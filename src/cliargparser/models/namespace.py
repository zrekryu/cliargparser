from typing import Any


class Namespace(dict[str, Any]):
    def __repr__(self) -> str:
        items_repr = ", ".join(
            f"{key}={value!r}"
            for key, value in self.items()
        )
        return (
            f"{type(self).__name__}"
            f"({items_repr})"
        )