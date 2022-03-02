from typing import Any, Callable, Set, List
import gc
import os
from queue import Queue, Empty
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial

import urwid


WORKER_THREADS = int(os.getenv("COBROWSER_WORKER_THREADS") or "2")
UI_POLL_INTERVAL = float(os.getenv("COBROWSER_UI_POLL_INTERVAL") or "0.2")


class Browser:
    def __init__(
        self, widget_ctor: Callable[["Browser"], urwid.Widget], gc_object_ids: Set[str]
    ):
        self._widget_ctor = widget_ctor
        self._gc_object_ids = gc_object_ids
        self._executor = None
        self._ui_poll_callbacks = Queue(maxsize=1000)

    def __enter__(self):
        self._executor = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="cobrowser-"
        )
        return self

    def __exit__(self, *_):
        self._executor.shutdown(cancel_futures=True, wait=True)

    def _toplevel_input(self, key: str):
        if key in ("q", "Q"):
            raise urwid.ExitMainLoop()

    def _on_ui_poll_interval(self, loop: urwid.MainLoop, _data=None):
        while True:
            try:
                cb = self._ui_poll_callbacks.get_nowait()
            except Empty:
                break
            cb()

        loop.set_alarm_in(UI_POLL_INTERVAL, self._on_ui_poll_interval)

    def saferepr(self, value: Any) -> str:
        out = repr(value)[:80]
        if len(out) == 80:
            out += "..."
        return out

    def saferepr_f(self, value: Any) -> Future[str]:
        return self._executor.submit(self.saferepr, value)

    def set_repr_later(
        self, value: Any, widget: urwid.Text, fmt: str = "{repr}"
    ) -> None:
        """Start calculating repr() for an object. Once done, arrange for the
        returned value to be set as text on the given widget.
        """
        f = self.saferepr_f(value)
        cb = partial(self._repr_done, widget=widget, fmt=fmt)
        f.add_done_callback(cb)

    def _repr_done(self, f: Future[str], *, widget: urwid.Text, fmt: str) -> None:
        if f.exception():
            rep = "repr error: %s" % type(f.exception()).__name__
        else:
            rep = f.result()

        text = fmt.format(repr=rep)

        cb = partial(widget.set_text, text)
        self.call_later(cb)

    def call_later(self, callback: Callable[[], Any]) -> None:
        self._ui_poll_callbacks.put(callback)

    def referents(self, x: Any) -> List[Any]:
        out = []
        for o in gc.get_referents(x):
            oid = id(o)
            if oid not in self._gc_object_ids:
                continue
            out.append(o)
        return out

    def referrers(self, x: Any) -> List[Any]:
        out = []
        for o in gc.get_referrers(x):
            oid = id(o)
            if oid not in self._gc_object_ids:
                continue
            out.append(o)
        return out

    def run(self):
        assert self._executor

        widget = self._widget_ctor(self)
        loop = urwid.MainLoop(widget, unhandled_input=self._toplevel_input)
        self._on_ui_poll_interval(loop)
        loop.run()
