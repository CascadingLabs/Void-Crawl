"""Type stubs for voidcrawl.actions.builtin.hover."""

from __future__ import annotations

from voidcrawl.actions._base import ActionNode, JsActionNode
from voidcrawl.actions._protocol import Tab

__all__ = ["CdpHover", "Hover"]

class Hover(JsActionNode):
    """Dispatch ``mouseenter`` + ``mouseover`` on an element via JS."""

    selector: str

    def __init__(self, selector: str) -> None: ...

class CdpHover(ActionNode):
    """Move the virtual mouse cursor to ``(x, y)`` via CDP ``mouseMoved``."""

    x: float
    y: float

    def __init__(self, x: float, y: float) -> None: ...
    async def run(self, tab: Tab) -> None: ...
