"""Headless Tk doubles and explicitly driven callbacks for App tests."""

from threading import Thread, get_ident, main_thread
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.App import App


class MainThreadMock(Mock):
    def __call__(self, *args, **kwargs):
        if get_ident() != main_thread().ident:
            raise AssertionError("Tk accessed outside the main thread")
        return super().__call__(*args, **kwargs)


class AppHarness:
    def __init__(self):
        self.pending = {}
        self.delays = []
        self.threads = []
        self.destroyed = False
        self.next_id = 0
        self.window = MainThreadMock()
        self.window.after.side_effect = self._after
        self.window.after_cancel.side_effect = self.pending.pop
        self.window.destroy.side_effect = self._destroy
        factories = {
            name: MainThreadMock(side_effect=lambda *args, **kwargs: MainThreadMock())
            for name in ("Label", "Entry", "Listbox", "Scrollbar", "Button", "Text", "Toplevel")
        }
        factories["Tk"] = MainThreadMock(return_value=self.window)
        with patch.multiple("app.App", **factories):
            self.app = App()

    def _after(self, delay, callback, *args):
        if self.destroyed:
            raise AssertionError("Callback scheduled after window destruction")
        self.next_id += 1
        self.delays.append(delay)
        self.pending[self.next_id] = (callback, args)
        return self.next_id

    def run_next(self):
        callback, args = self.pending.pop(next(iter(self.pending)))
        callback(*args)

    def emit(self, widget, sequence):
        for binding in widget.bind.call_args_list:
            if binding.args[0] == sequence:
                binding.args[1](SimpleNamespace(widget=widget))

    def _destroy(self):
        self.emit(self.window, "<Destroy>")
        self.destroyed = True

    def close(self):
        for protocol in self.window.protocol.call_args_list:
            if protocol.args[0] == "WM_DELETE_WINDOW":
                protocol.args[1]()
                return
        raise AssertionError("No window close handler registered")

    def new_thread(self, *args, **kwargs):
        worker = Thread(*args, **kwargs)
        self.threads.append(worker)
        return worker

    def finish_workers(self, testcase):
        for worker in self.threads:
            worker.join(timeout=5)
            testcase.assertFalse(worker.is_alive(), "Worker did not finish")
