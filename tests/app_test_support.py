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
        self.dialogs = []
        self.entries = []
        self.buttons = []
        self.live_dialogs = set()
        self.destroyed = False
        self.next_id = 0
        self.window = MainThreadMock()
        self.window.after.side_effect = self._after
        self.window.after_cancel.side_effect = self.pending.pop
        self.window.destroy.side_effect = self._destroy
        self.factories = {
            name: MainThreadMock(side_effect=lambda *args, **kwargs: MainThreadMock())
            for name in ("Label", "Entry", "Listbox", "Scrollbar", "Button", "Text", "Toplevel")
        }
        self.factories["Tk"] = MainThreadMock(return_value=self.window)
        self.factories["Toplevel"].side_effect = self._toplevel
        self.factories["Entry"].side_effect = self._entry
        self.factories["Button"].side_effect = self._button
        with self.patch_widgets():
            self.app = App()

    def patch_widgets(self):
        return patch.multiple("app.App", **self.factories)

    def _entry(self, master, *args, **kwargs):
        entry = MainThreadMock()
        object.__setattr__(entry, "master", master)
        self.entries.append(entry)
        return entry

    def _button(self, master=None, *args, **kwargs):
        button = MainThreadMock()
        button.invoke.side_effect = kwargs.get("command")
        self.buttons.append(button)
        return button

    def _toplevel(self, master=None):
        dialog = MainThreadMock()
        object.__setattr__(dialog, "master", master)
        self.dialogs.append(dialog)
        self.live_dialogs.add(id(dialog))

        def destroy():
            if id(dialog) not in self.live_dialogs:
                raise AssertionError("Dialog destroyed more than once")
            self.live_dialogs.remove(id(dialog))
            self.emit(dialog, "<Destroy>")

        dialog.destroy.side_effect = destroy
        return dialog

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
        for dialog in self.dialogs:
            if id(dialog) in self.live_dialogs:
                dialog.destroy()
        self.emit(self.window, "<Destroy>")
        self.destroyed = True

    def close(self, widget=None):
        widget = self.window if widget is None else widget
        for protocol in widget.protocol.call_args_list:
            if protocol.args[0] == "WM_DELETE_WINDOW":
                protocol.args[1]()
                return
        widget.destroy()

    def new_thread(self, *args, **kwargs):
        worker = Thread(*args, **kwargs)
        self.threads.append(worker)
        return worker

    def finish_workers(self, testcase):
        for worker in self.threads:
            worker.join(timeout=5)
            testcase.assertFalse(worker.is_alive(), "Worker did not finish")
