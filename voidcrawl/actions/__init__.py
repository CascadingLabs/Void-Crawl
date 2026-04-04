"""Extensible browser actions backed by JavaScript or CDP commands.

This sub-package exposes two tiers of actions:

* **JS-tier** — actions evaluated as JavaScript inside the page
  (subclass :class:`JsActionNode`).
* **CDP-tier** — actions that call Chrome DevTools Protocol input
  methods directly (subclass :class:`ActionNode`).

Actions can be composed into :class:`Flow` sequences and executed
against any object satisfying the :class:`Tab` protocol (both
:class:`~voidcrawl.Page` and :class:`~voidcrawl.PooledTab`).

Custom actions are created by subclassing :class:`ActionNode` or
:class:`JsActionNode` and implementing :meth:`~ActionNode.run`.
"""

from voidcrawl.actions._base import (
    ActionNode,
    JsActionNode,
    JsSource,
    inline_js,
    load_js,
)
from voidcrawl.actions._flow import Flow, FlowResult
from voidcrawl.actions._protocol import JsTab, Tab
from voidcrawl.actions.builtin import (
    CdpClick,
    CdpClickAndHold,
    CdpHover,
    CdpScroll,
    CdpScrollDown,
    CdpScrollLeft,
    CdpScrollRight,
    CdpScrollUp,
    CdpTypeText,
    ClearInput,
    ClickAt,
    ClickElement,
    GetAttribute,
    GetText,
    Hover,
    ScrollBy,
    ScrollTo,
    SelectOption,
    SetAttribute,
    SetInputValue,
    WaitForSelector,
    WaitForTimeout,
)

__all__ = [
    # framework
    "ActionNode",
    "CdpClick",
    "CdpClickAndHold",
    "CdpHover",
    "CdpScroll",
    "CdpScrollDown",
    "CdpScrollLeft",
    "CdpScrollRight",
    "CdpScrollUp",
    "CdpTypeText",
    "ClearInput",
    # builtin - click
    "ClickAt",
    "ClickElement",
    "Flow",
    "FlowResult",
    # builtin - dom
    "GetAttribute",
    "GetText",
    # builtin - hover
    "Hover",
    "JsActionNode",
    "JsSource",
    "JsTab",
    "ScrollBy",
    # builtin - scroll
    "ScrollTo",
    "SelectOption",
    "SetAttribute",
    # builtin - input
    "SetInputValue",
    "Tab",
    # builtin - wait
    "WaitForSelector",
    "WaitForTimeout",
    "inline_js",
    "load_js",
]
