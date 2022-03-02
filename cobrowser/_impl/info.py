from typing import Any
import urwid

from .browser import Browser
from . import gcnodes


def haslen(value) -> bool:
    if isinstance(value, (list, set, dict, tuple, str, bytes)):
        return True
    return False


class TypeInfoNode(urwid.TreeNode):
    def __init__(self, browser: Browser, **kwargs):
        super().__init__(**kwargs)

    def load_widget(self):
        text = "type: %s" % type(self.get_value()).__name__
        out = super().load_widget()
        out.get_inner_widget().set_text(text)
        return out


class LenInfoNode(urwid.TreeNode):
    def __init__(self, browser: Browser, **kwargs):
        super().__init__(**kwargs)

    def load_widget(self):
        text = "len: %s" % len(self.get_value())
        out = super().load_widget()
        out.get_inner_widget().set_text(text)
        return out


class ReprInfoNode(urwid.TreeNode):
    def __init__(self, browser: Browser, **kwargs):
        self.__browser = browser
        super().__init__(**kwargs)

    def load_widget(self):
        text = "repr: loading..."
        out = super().load_widget()
        inner = out.get_inner_widget()
        inner.set_text(text)

        self.__browser.set_repr_later(self.get_value(), inner, fmt="repr: {repr}")

        return out


class CycleInfoNode(urwid.TreeNode):
    def __init__(self, browser: Browser, **kwargs):
        super().__init__(**kwargs)

    def load_widget(self):
        text = "cycle: see %s nodes above" % self.get_parent().cycle_depth
        out = super().load_widget()
        out.get_inner_widget().set_text(text)
        return out


class InfoNode(urwid.ParentNode):
    """Top-level parent node associated with an object, holding child nodes
    with more detailed information (including references to other objects).
    """

    def __init__(self, *, value: Any, parent: Any, browser, key: Any = None):
        self.__browser = browser
        key = "info-%x" % id(value)
        super().__init__(value, key=key, parent=parent)

    @property
    def cycle_depth(self) -> int:
        out = 0
        parent = self.get_parent()
        while parent:
            out += 1
            if parent.get_key() == self.get_key():
                return out
            parent = parent.get_parent()
        return 0

    def load_widget(self):
        return InfoTreeWidget(self)

    def load_child_keys(self):
        if self.cycle_depth:
            return ["cycle"]

        out = ["type"]
        if haslen(self.get_value()):
            out.append("len")
        out.append("repr")
        out.append("refs")
        out.append("refnts")
        return out

    def load_child_node(self, key):
        klass = None

        node_types = {
            "type": TypeInfoNode,
            "len": LenInfoNode,
            "repr": ReprInfoNode,
            "refnts": gcnodes.GcReferentsNode,
            "refs": gcnodes.GcReferrersNode,
            "cycle": CycleInfoNode,
        }

        klass = node_types.get(key)
        assert klass, "Unexpected key %s" % key

        return klass(
            value=self.get_value(), parent=self, key=key, browser=self.__browser
        )


class InfoTreeWidget(urwid.TreeWidget):
    def get_display_text(self) -> str:
        val = self.get_node().get_value()
        return "<%s 0x%x>" % (
            type(val).__name__,
            id(val),
        )
