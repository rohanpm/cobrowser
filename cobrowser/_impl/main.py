from typing import Any
import gc

import urwid

from .limits import memlimit
from .widgets import BrowserListBox
from .browser import Browser


def browse(root: Any, *, enable_memlimit=True):
    gc_object_ids = set([id(o) for o in gc.get_objects()])

    if enable_memlimit:
        memlimit()

    def ctor(browser):
        return urwid.Frame(body=BrowserListBox(root, browser))

    with Browser(widget_ctor=ctor, gc_object_ids=gc_object_ids) as browser:
        browser.run()
