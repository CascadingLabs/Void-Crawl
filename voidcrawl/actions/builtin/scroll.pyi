"""Type stubs for voidcrawl.actions.builtin.scroll."""

from __future__ import annotations

from voidcrawl.actions._base import ActionNode, JsActionNode
from voidcrawl.actions._protocol import Tab

__all__ = [
    "CdpScroll",
    "CdpScrollDown",
    "CdpScrollLeft",
    "CdpScrollRight",
    "CdpScrollUp",
    "ScrollBy",
    "ScrollTo",
]

class ScrollTo(JsActionNode):
    """Scroll the window to an absolute position via ``window.scrollTo``."""

    x: int
    y: int

    def __init__(self, x: int = 0, y: int = 0) -> None: ...

class ScrollBy(JsActionNode):
    """Scroll the window by a relative offset via ``window.scrollBy``."""

    dx: int
    dy: int

    def __init__(self, dx: int = 0, dy: int = 0) -> None: ...

class CdpScroll(ActionNode):
    """Scroll via a CDP ``mouseWheel`` event fired at ``(x, y)``."""

    x: float
    y: float
    delta_x: float
    delta_y: float

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        delta_x: float = 0,
        delta_y: float = 0,
    ) -> None: ...
    async def run(self, tab: Tab) -> None: ...

class CdpScrollDown(CdpScroll):
    """Scroll **down** by *pixels* at ``(x, y)`` via CDP."""

    def __init__(self, pixels: float = 100, x: float = 0, y: float = 0) -> None: ...

class CdpScrollUp(CdpScroll):
    """Scroll **up** by *pixels* at ``(x, y)`` via CDP."""

    def __init__(self, pixels: float = 100, x: float = 0, y: float = 0) -> None: ...

class CdpScrollRight(CdpScroll):
    """Scroll **right** by *pixels* at ``(x, y)`` via CDP."""

    def __init__(self, pixels: float = 100, x: float = 0, y: float = 0) -> None: ...

class CdpScrollLeft(CdpScroll):
    """Scroll **left** by *pixels* at ``(x, y)`` via CDP."""

    def __init__(self, pixels: float = 100, x: float = 0, y: float = 0) -> None: ...
