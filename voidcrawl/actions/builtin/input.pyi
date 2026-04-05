"""Type stubs for voidcrawl.actions.builtin.input."""

from __future__ import annotations

from voidcrawl.actions._base import ActionNode, JsActionNode
from voidcrawl.actions._protocol import Tab

__all__ = ["CdpTypeText", "ClearInput", "SelectOption", "SetInputValue"]

class SetInputValue(JsActionNode):
    """Bulk-set an input's value and fire ``input``/``change`` events."""

    selector: str
    text: str

    def __init__(self, selector: str, text: str) -> None: ...

class ClearInput(JsActionNode):
    """Clear an input field and fire an ``input`` event via JS."""

    selector: str

    def __init__(self, selector: str) -> None: ...

class SelectOption(JsActionNode):
    """Select a ``<select>`` option by value and fire a ``change`` event."""

    selector: str
    value: str

    def __init__(self, selector: str, value: str) -> None: ...

class CdpTypeText(ActionNode):
    """Type *text* character-by-character via CDP ``Input.dispatchKeyEvent``."""

    text: str

    def __init__(self, text: str) -> None: ...
    async def run(self, tab: Tab) -> None: ...
