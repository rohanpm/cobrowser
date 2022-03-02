from typing import Any
import urwid


from .info import InfoNode
from .browser import Browser


class BrowserWalker(urwid.TreeWalker):
    def __init__(self, root: Any, browser: Browser):
        super().__init__(InfoNode(value=root, browser=browser, parent=None))


class BrowserListBox(urwid.TreeListBox):
    def __init__(self, root: Any, browser: Browser):
        self.__browser = browser
        super().__init__(body=BrowserWalker(root, self.__browser))
