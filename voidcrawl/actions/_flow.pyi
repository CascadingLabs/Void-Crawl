"""Type stubs for voidcrawl.actions._flow."""

from __future__ import annotations

from voidcrawl.actions._base import ActionNode
from voidcrawl.actions._protocol import Tab

__all__ = ["Flow", "FlowResult"]

class FlowResult:
    """Aggregated result of a :class:`Flow` execution."""

    results: list[object]

    def __init__(self, results: list[object] = ...) -> None: ...
    @property
    def last(self) -> object:
        """The return value of the final action, or ``None`` for empty flows."""
        ...

class Flow:
    """An ordered sequence of actions executed against a single tab."""

    def __init__(self, actions: list[ActionNode] | None = None) -> None: ...
    def add(self, action: ActionNode) -> Flow:
        """Append an action and return *self* for chaining."""
        ...

    def __len__(self) -> int: ...
    async def run(self, tab: Tab) -> FlowResult:
        """Execute all actions sequentially against *tab*."""
        ...
