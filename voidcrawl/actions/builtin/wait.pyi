"""Type stubs for voidcrawl.actions.builtin.wait."""

from __future__ import annotations

from voidcrawl.actions._base import JsActionNode

__all__ = ["WaitForSelector", "WaitForTimeout"]

class WaitForSelector(JsActionNode):
    """Poll until a CSS selector matches an element, with timeout.

    Throws a JS ``Error`` when *timeout* seconds elapse without a match.
    """

    selector: str
    timeout: float

    def __init__(self, selector: str, timeout: float = 10.0) -> None: ...

class WaitForTimeout(JsActionNode):
    """Sleep for *ms* milliseconds **inside the browser context**."""

    ms: int

    def __init__(self, ms: int) -> None: ...
