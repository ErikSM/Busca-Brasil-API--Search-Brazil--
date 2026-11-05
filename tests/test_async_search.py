import unittest
from threading import Event, get_ident
from types import SimpleNamespace
from unittest.mock import call, patch

from access import addresses
from access.requests import requests
from app import menus
from app_test_support import AppHarness


class AsyncSearchTests(unittest.TestCase):
    def setUp(self):
        self.gui = AppHarness()
        self.app = self.gui.app
        self.main_thread = get_ident()
        self.network = patch("access.requests.requests.get", side_effect=AssertionError("Real HTTP forbidden"))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.client = patch("app.App.open_dict")
        self.open_dict = self.client.start()
        self.addCleanup(self.client.stop)
        self.worker_patch = patch("app.App.Thread", side_effect=self.gui.new_thread)
        self.worker_patch.start()
        self.addCleanup(self.worker_patch.stop)
        self.addCleanup(self.gui.finish_workers, self)

    def select(self, operation="Todos os bancos", catalog=addresses.bank_and_stockbroker):
        self.app.dict_selected = catalog
        self.app.listbox_left.get.return_value = operation
        self.app.listbox_left.curselection.return_value = (
            (tuple(catalog).index(operation),) if operation in catalog else ()
        )
        self.app.search()

    def delayed_response(self, result=None, error=None):
        started, release = Event(), Event()
        self.addCleanup(release.set)

        def fetch(*args):
            self.assertNotEqual(get_ident(), self.main_thread)
            started.set()
            if not release.wait(timeout=5):
                raise AssertionError("Test did not release HTTP response")
            if error is not None:
                raise error
            return result

        return fetch, started, release

    def complete(self):
        self.gui.finish_workers(self)
        self.assertEqual(len(self.gui.pending), 1)
        self.gui.run_next()
        self.assertFalse(self.gui.pending)

    def test_list_and_dictionary_keep_existing_presentation_on_main_thread(self):
        for response in ([{"nome": "Banco A"}, {"nome": "Banco B"}], {"code": 1, "name": "Banco A"}, []):
            with self.subTest(response=response):
                self.app.listbox_right.reset_mock()

                def fetch(address):
                    self.assertNotEqual(get_ident(), self.main_thread)
                    return response

                self.open_dict.side_effect = fetch
                self.select()
                self.gui.finish_workers(self)
                self.app.listbox_right.insert.assert_not_called()
                self.assertEqual(len(self.gui.pending), 1)
                self.gui.run_next()
                self.assertEqual(self.app.listbox_right.insert.call_args_list,
                                 [call("end", item) for item in response])
                self.assertFalse(self.gui.pending)
                self.assertTrue(all(worker.daemon for worker in self.gui.threads))

    def test_http_error_preserves_existing_message_on_main_thread(self):
        failure = requests.exceptions.HTTPError("503 Service Unavailable")
        self.open_dict.side_effect = failure
        self.select()
        self.app.text.reset_mock()
        self.complete()
        self.app.text.delete.assert_called_once_with(1.0, "end")
        self.app.text.insert.assert_called_once_with("end", failure)
        self.app.listbox_right.insert.assert_not_called()

    def test_delayed_http_does_not_block_and_polls_only_while_pending(self):
        fetch, started, release = self.delayed_response(["concluido"])
        self.open_dict.side_effect = fetch
        self.select()
        self.assertTrue(started.wait(timeout=5))
        self.assertFalse(release.is_set())
        self.assertEqual(len(self.gui.pending), 1)
        self.gui.run_next()
        self.assertEqual(len(self.gui.pending), 1)
        self.assertTrue(all(delay >= 100 for delay in self.gui.delays))
        self.app.listbox_right.insert.assert_not_called()
        self.app.print_text("interface continua ativa")
        release.set()
        self.complete()
        self.app.listbox_right.insert.assert_called_once_with("end", "concluido")

    def test_older_success_or_error_cannot_replace_newer_result(self):
        for failure in (None, requests.exceptions.HTTPError("old failure")):
            with self.subTest(failure=failure):
                fetch, started, release = self.delayed_response(["antigo"], failure)
                self.open_dict.side_effect = fetch
                self.select()
                self.assertTrue(started.wait(timeout=5))
                stale_callback, stale_args = next(iter(self.gui.pending.values()))
                self.open_dict.side_effect = None
                self.open_dict.return_value = ["novo"]
                self.select("Todas as Corretoras")
                stale_callback(*stale_args)
                self.assertEqual(len(self.gui.pending), 1)
                release.set()
                self.complete()
                self.app.listbox_right.insert.assert_called_once_with("end", "novo")
                self.app.text.reset_mock()
                self.app.listbox_right.reset_mock()
                stale_callback(*stale_args)
                self.app.text.insert.assert_not_called()
                self.app.listbox_right.insert.assert_not_called()
                self.assertFalse(self.gui.pending)

    def test_repeated_same_operation_keeps_only_latest_request(self):
        fetch, started, release = self.delayed_response(["antigo"])
        self.open_dict.side_effect = fetch
        self.select()
        self.assertTrue(started.wait(timeout=5))
        self.open_dict.side_effect = None
        self.open_dict.return_value = ["novo"]
        self.select()
        release.set()
        self.complete()
        self.app.listbox_right.insert.assert_called_once_with("end", "novo")

    def test_changed_list_selection_invalidates_pending_request(self):
        fetch, started, release = self.delayed_response(["antigo"])
        self.open_dict.side_effect = fetch
        self.select()
        self.assertTrue(started.wait(timeout=5))
        self.app.listbox_left.get.return_value = "Banco por codigo"
        self.app.listbox_left.curselection.return_value = (1,)
        self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
        self.assertFalse(self.gui.pending)
        release.set()
        self.gui.finish_workers(self)
        self.app.listbox_right.insert.assert_not_called()

    def test_keyboard_or_drag_selection_invalidates_even_with_unchanged_anchor(self):
        fetch, started, release = self.delayed_response(["antigo"])
        self.open_dict.side_effect = fetch
        self.select()
        self.assertTrue(started.wait(timeout=5))
        callback, args = next(iter(self.gui.pending.values()))
        # Tk browse mode moves the selection without moving the anchor.
        self.app.listbox_left.curselection.return_value = (1,)
        self.assertEqual(self.app.listbox_left.get("anchor"), "Todos os bancos")
        self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
        self.assertFalse(self.gui.pending)
        release.set()
        self.gui.finish_workers(self)
        callback(*args)
        self.app.listbox_right.insert.assert_not_called()

    def test_same_list_selection_does_not_cancel_current_request(self):
        self.open_dict.return_value = ["atual"]
        self.select()
        self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
        self.complete()
        self.app.listbox_right.insert.assert_called_once_with("end", "atual")

    def test_category_change_invalidates_request_even_when_returning_to_category(self):
        fetch, started, release = self.delayed_response(["antigo"])
        self.open_dict.side_effect = fetch
        self.select()
        self.assertTrue(started.wait(timeout=5))
        menus._select_menu(self.app, menus.menus_list["Taxes"])
        menus._select_menu(self.app, menus.menus_list["Bank/Stockbroker"])
        self.assertFalse(self.gui.pending)
        release.set()
        self.gui.finish_workers(self)
        self.app.listbox_right.insert.assert_not_called()

    def test_parameterized_search_stays_synchronous_and_invalidates_old_result(self):
        fetch, started, release = self.delayed_response(["antigo"])
        self.open_dict.side_effect = fetch
        self.select()
        self.assertTrue(started.wait(timeout=5))
        with patch.object(self.app, "_quick_window") as quick:
            self.select("Banco por codigo")
        quick.assert_called_once_with("Banco por codigo")
        self.assertFalse(self.gui.pending)
        self.app.selected_operation = "Banco por codigo"
        self.app.field_toplevel = self.app.listbox_right
        self.app.entry.get.return_value = "001"

        def parameterized(address, parameter):
            self.assertEqual(get_ident(), self.main_thread)
            self.assertEqual(parameter, "001")
            return {"nome": "novo"}

        self.open_dict.side_effect = parameterized
        self.app._get_to_quick_window(self.app.entry)
        release.set()
        self.gui.finish_workers(self)
        self.assertEqual(self.app.listbox_right.insert.call_args_list,
                         [call("end", "nome"), call("end", "novo"), call("end", "\n")])

    def test_invalid_search_invalidates_pending_result(self):
        fetch, started, release = self.delayed_response(["antigo"])
        self.open_dict.side_effect = fetch
        self.select()
        self.assertTrue(started.wait(timeout=5))
        self.select("operacao inexistente")
        self.assertFalse(self.gui.pending)
        release.set()
        self.gui.finish_workers(self)
        self.app.listbox_right.insert.assert_called_once_with("end", "Erro de acesso")

    def test_close_while_pending_cancels_callback_and_ignores_late_response(self):
        fetch, started, release = self.delayed_response(["tarde demais"])
        self.open_dict.side_effect = fetch
        self.select()
        self.assertTrue(started.wait(timeout=5))
        callback, args = next(iter(self.gui.pending.values()))
        self.gui.close()
        self.assertTrue(self.gui.destroyed)
        self.assertFalse(self.gui.pending)
        self.assertFalse(release.is_set())
        self.app.text.reset_mock()
        self.app.listbox_right.reset_mock()
        release.set()
        self.gui.finish_workers(self)
        callback(*args)
        self.app.search()
        self.app.text.insert.assert_not_called()
        self.app.listbox_right.insert.assert_not_called()
        self.assertFalse(self.gui.pending)
        self.assertEqual(len(self.gui.threads), 1)

    def test_external_window_destruction_also_cancels_pending_callback(self):
        self.open_dict.return_value = ["descartar"]
        self.select()
        self.gui.finish_workers(self)
        self.gui.window.destroy()
        self.assertFalse(self.gui.pending)
        self.app.listbox_right.insert.assert_not_called()

    def test_child_destruction_does_not_cancel_request(self):
        self.open_dict.return_value = ["atual"]
        self.select()
        for binding in self.gui.window.bind.call_args_list:
            if binding.args[0] == "<Destroy>":
                binding.args[1](SimpleNamespace(widget=self.app.listbox_right))
        self.complete()
        self.app.listbox_right.insert.assert_called_once_with("end", "atual")
