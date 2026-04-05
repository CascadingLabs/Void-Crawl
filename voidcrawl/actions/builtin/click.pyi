"""Type stubs for voidcrawl.actions.builtin.click."""

from __future__ import annotations

from voidcrawl.actions._base import ActionNode, JsActionNode
from voidcrawl.actions._protocol import Tab

__all__ = ["CdpClick", "CdpClickAndHold", "ClickAt", "ClickElement"]

class ClickAt(JsActionNode):
    """Click the element at page coordinates ``(x, y)`` via JS events."""

    x: int
    y: int

    def __init__(self, x: int, y: int) -> None: ...

class ClickElement(JsActionNode):
    """Click the first element matching a CSS *selector* via JS.

    Raises a JS ``Error`` if no element matches.
    """

    selector: str

    def __init__(self, selector: str) -> None: ...

class CdpClick(ActionNode):
    """Click at ``(x, y)`` via CDP ``Input.dispatchMouseEvent``.

    Sends ``mousePressed`` followed by ``mouseReleased``.
    """

    x: float
    y: float
    button: str

    def __init__(self, x: float, y: float, button: str = "left") -> None: ...
    async def run(self, tab: Tab) -> None: ...

class CdpClickAndHold(ActionNode):
    """Mouse-down, hold for *duration_ms*, then mouse-up via CDP."""

    x: float
    y: float
    duration_ms: int
    button: str

    def __init__(
        self,
        x: float,
        y: float,
        duration_ms: int = 500,
        button: str = "left",
    ) -> None: ...
    async def run(self, tab: Tab) -> None: ...
