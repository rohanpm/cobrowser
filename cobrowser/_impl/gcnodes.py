from typing import Any, Callable, List
import urwid

from .browser import Browser
from . import info


class GcReferentsTreeWidget(urwid.TreeWidget):
    def get_display_text(self) -> str:
        return "refnts: %d" % len(self.get_node().get_child_keys())


class GcReferrersTreeWidget(urwid.TreeWidget):
    def get_display_text(self) -> str:
        return "refs: %d" % len(self.get_node().get_child_keys())


class GcNode(urwid.ParentNode):
    def __init__(
        self,
        *,
        value: Any,
        key: Any,
        parent: Any,
        browser: Browser,
        get_refs: Callable[[Any], List[Any]],
        widget_type: Callable[[urwid.TreeNode], urwid.TreeWidget]
    ):
        self.__browser = browser
        self.__objects_by_key = {}
        self.__get_refs = get_refs
        self.__widget_type = widget_type
        super().__init__(value, key=key, parent=parent)
        self.expanded = False

    def load_widget(self):
        out = self.__widget_type(self)
        out.expanded = False
        out.update_expanded_icon()
        return out

    def load_child_keys(self):
        for obj in self.__get_refs(self.get_value()):
            key = "info-%x" % id(obj)
            self.__objects_by_key[key] = obj
        # TODO: maybe support some other sorting e.g. by type?
        return sorted(self.__objects_by_key.keys())

    def load_child_node(self, key):
        obj = self.__objects_by_key[key]

        return info.InfoNode(value=obj, parent=self, key=key, browser=self.__browser)


class GcReferentsNode(GcNode):
    def __init__(self, **kwargs):
        super().__init__(
            get_refs=kwargs["browser"].referents,
            widget_type=GcReferentsTreeWidget,
            **kwargs
        )


class GcReferrersNode(GcNode):
    def __init__(self, **kwargs):
        super().__init__(
            get_refs=kwargs["browser"].referrers,
            widget_type=GcReferrersTreeWidget,
            **kwargs
        )
