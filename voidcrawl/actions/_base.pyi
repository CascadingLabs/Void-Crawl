"""Type stubs for voidcrawl.actions._base."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from voidcrawl.actions._protocol import JsTab, Tab

__all__ = ["ActionNode", "JsActionNode", "JsSource", "inline_js", "load_js"]

class JsSource:
    """Immutable wrapper around a JavaScript snippet string."""

    def __init__(self, js: str) -> None: ...
    @property
    def js(self) -> str:
        """The raw JavaScript source string."""
        ...

def load_js(path: str | Path) -> JsSource:
    """Load JavaScript from a ``.js`` file on disk.

    Relative paths are resolved from the **caller's** source file.
    """
    ...

def inline_js(code: str) -> JsSource:
    """Create a :class:`JsSource` from an inline string literal."""
    ...

class ActionNode(ABC):
    """Abstract base for all browser actions.

    Subclass and implement :meth:`run` to create a custom action.
    """

    @abstractmethod
    async def run(self, tab: Tab) -> object:
        """Execute this action against *tab*."""
        ...

class JsActionNode(ActionNode):
    """Action executed by evaluating a JavaScript snippet in the page.

    Subclasses set the ``js`` class attribute via :func:`load_js` or
    :func:`inline_js` and store their parameters as instance attributes.
    """

    js: JsSource

    def params(self) -> dict[str, Any]:
        """Return the parameters injected as ``__params`` in the JS snippet."""
        ...

    async def run(self, tab: JsTab) -> object:
        """Evaluate the JS snippet in *tab* with the current :meth:`params`."""
        ...
