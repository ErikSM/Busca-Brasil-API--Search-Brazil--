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
        self.widget_patch = self.gui.patch_widgets()
        self.widget_patch.start()
        self.addCleanup(self.widget_patch.stop)
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

    def parameter_form(self, value="001", operation="Banco por codigo",
                       catalog=addresses.bank_and_stockbroker):
        self.select(operation, catalog)
        dialog = self.app.field_toplevel
        entry = self.gui.entries[-1]
        entry.get.return_value = value
        return dialog, entry, self.gui.buttons[-1].invoke

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

    def test_parameterized_search_is_asynchronous_and_invalidates_old_result(self):
        fetch, started, release = self.delayed_response(["antigo"])
        self.open_dict.side_effect = fetch
        self.select()
        self.assertTrue(started.wait(timeout=5))
        dialog, entry, submit = self.parameter_form()
        self.assertFalse(self.gui.pending)

        def parameterized(address, parameter):
            self.assertNotEqual(get_ident(), self.main_thread)
            self.assertEqual(parameter, "001")
            return {"nome": "novo"}

        self.open_dict.side_effect = parameterized
        submit()
        dialog.destroy.assert_not_called()
        release.set()
        self.complete()
        dialog.destroy.assert_called_once()
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

    def test_parameter_form_uses_root_event_loop_and_replaces_previous_dialog(self):
        old, old_entry, old_submit = self.parameter_form()
        old.mainloop.assert_not_called()
        self.assertIs(old.master, self.gui.window)
        current, entry, submit = self.parameter_form("002")
        old.destroy.assert_called_once()
        self.assertEqual(self.gui.live_dialogs, {id(current)})
        old_entry.reset_mock()
        old_submit()
        old_entry.get.assert_not_called()
        self.open_dict.assert_not_called()
        self.assertIs(self.app.field_toplevel, current)

    def test_parameter_validation_precedes_thread_creation_and_normalizes_all_operations(self):
        values = {
            "Busca por CEP": ("12345-678", "12345678"),
            "Busca por DDD": ("01", "01"),
            "Feriados por ano": ("2026", "2026"),
            "Busca por CNPJ": ("12.abc.345/01de-35", "12ABC34501DE35"),
            "Busca Livro por ISNB": ("0-306-40615-2", "0306406152"),
            "Banco por codigo": (" 001 ", "001"),
            "Corretoras por CNPJ": ("12.abc.345/01de-35", "12ABC34501DE35"),
            "Busca por Dominio BR": (" WWW.Exemplo.BR ", "www.exemplo.br"),
            "CPTEC por cidade": (" São José dos Campos ", "São José dos Campos"),
            "Clima em aeroportos por codigo": (" sbgr ", "SBGR"),
            "Clima em cidade por codigo": (" 001 ", "001"),
            "Onda em cidade por codigo": (" 001 ", "001"),
            "Marcas por caminhoes, carros ou moto": (" CARROS ", "carros"),
            "Preco de veiculo por codigo FIPE": (" 001004-9 ", "001004-9"),
            "Produto por codigo": ("0101.21.00", "01012100"),
            "Taxa por sigla": (" selic ", "SELIC"),
        }
        for catalog, _ in menus.menus_list.values():
            for operation, (url, needs_parameter, _) in catalog.items():
                if not needs_parameter:
                    continue
                with self.subTest(operation=operation):
                    raw, normalized = values[operation]
                    dialog, entry, submit = self.parameter_form(raw, operation, catalog)
                    self.open_dict.reset_mock()

                    def fetch(address, parameter):
                        self.assertNotEqual(get_ident(), self.main_thread)
                        return []

                    self.open_dict.side_effect = fetch
                    submit()
                    self.complete()
                    self.open_dict.assert_called_once_with(url, normalized)
                    dialog.destroy.assert_called_once()

    def test_invalid_parameter_creates_no_worker_and_closes_dialog(self):
        dialog, entry, submit = self.parameter_form("invalid")
        submit()
        self.open_dict.assert_not_called()
        self.assertFalse(self.gui.threads)
        self.assertFalse(self.gui.pending)
        dialog.destroy.assert_called_once()
        self.assertIsNone(self.app.field_toplevel)

    def test_parameter_list_dictionary_and_empty_results_keep_presentation(self):
        for response, expected in (
            ([{"nome": "Banco"}, "outro"], [{"nome": "Banco"}, "\n", "outro", "\n"]),
            ({"code": "001", "items": ["A", "B"], "nested": {"x": 1}},
             ["code", "001", "\n", "items", "A", "B", "\n", "nested", {"x": 1}, "\n"]),
            ([], []), ({}, []),
        ):
            with self.subTest(response=response):
                dialog, entry, submit = self.parameter_form()
                self.app.listbox_right.reset_mock()
                self.open_dict.return_value = response
                submit()
                self.gui.finish_workers(self)
                self.app.listbox_right.insert.assert_not_called()
                dialog.destroy.assert_not_called()
                self.complete()
                self.assertEqual(self.app.listbox_right.insert.call_args_list,
                                 [call("end", item) for item in expected])
                dialog.destroy.assert_called_once()

    def test_parameter_http_error_keeps_message_and_closes_dialog(self):
        dialog, entry, submit = self.parameter_form()
        self.open_dict.side_effect = requests.exceptions.HTTPError("bad status")
        submit()
        self.app.text.reset_mock()
        self.complete()
        self.app.text.insert.assert_called_once_with("end", "Error:bad status   \n\n-Em branco ou invalido")
        self.app.listbox_right.insert.assert_called_once_with("end", "Erro de acesso")
        dialog.destroy.assert_called_once()

    def test_slow_parameter_request_keeps_ui_responsive_and_parameter_snapshot(self):
        dialog, entry, submit = self.parameter_form(" 001 ")
        fetch, started, release = self.delayed_response(["done"])
        self.open_dict.side_effect = fetch
        submit()
        self.assertTrue(started.wait(timeout=5))
        self.assertFalse(release.is_set())
        dialog.destroy.assert_not_called()
        self.gui.run_next()
        self.assertEqual(len(self.gui.pending), 1)
        self.app.print_text("interface ativa")
        entry.get.return_value = "002"
        release.set()
        self.complete()
        self.open_dict.assert_called_once_with(addresses.bank_and_stockbroker["Banco por codigo"][0], "001")
        entry.get.assert_called_once()
        self.assertTrue(all(delay >= 100 for delay in self.gui.delays))
        dialog.destroy.assert_called_once()

    def test_successive_parameters_out_of_order_keep_only_new_result(self):
        for error in (None, requests.exceptions.HTTPError("old error")):
            with self.subTest(error=error):
                dialog, entry, submit = self.parameter_form("001")
                fetch, started, release = self.delayed_response(["old"], error)
                self.open_dict.side_effect = fetch
                submit()
                self.assertTrue(started.wait(timeout=5))
                stale, args = next(iter(self.gui.pending.values()))
                old_worker = self.gui.threads[-1]
                entry.get.return_value = "002"
                self.open_dict.side_effect = None
                self.open_dict.return_value = ["new"]
                submit()
                self.gui.threads[-1].join(timeout=5)
                self.assertFalse(self.gui.threads[-1].is_alive())
                self.assertTrue(old_worker.is_alive())
                self.assertEqual(len(self.gui.pending), 1)
                self.app.listbox_right.reset_mock()
                self.gui.run_next()
                self.assertEqual(self.app.listbox_right.insert.call_args_list,
                                 [call("end", "new"), call("end", "\n")])
                dialog.destroy.assert_called_once()
                self.app.text.reset_mock()
                self.app.listbox_right.reset_mock()
                release.set()
                self.gui.finish_workers(self)
                stale(*args)
                self.app.text.insert.assert_not_called()
                self.app.listbox_right.insert.assert_not_called()
                self.assertFalse(self.gui.pending)

    def test_invalid_resubmission_invalidates_pending_valid_response(self):
        dialog, entry, submit = self.parameter_form()
        fetch, started, release = self.delayed_response(["old"])
        self.open_dict.side_effect = fetch
        submit()
        self.assertTrue(started.wait(timeout=5))
        stale, args = next(iter(self.gui.pending.values()))
        entry.get.return_value = "invalid"
        submit()
        self.assertEqual(len(self.gui.threads), 1)
        self.assertFalse(self.gui.pending)
        dialog.destroy.assert_called_once()
        release.set()
        self.gui.finish_workers(self)
        self.app.text.reset_mock()
        stale(*args)
        self.app.text.insert.assert_not_called()
        self.app.listbox_right.insert.assert_not_called()

    def test_close_dialog_during_request_discards_result_and_stale_submit(self):
        dialog, entry, submit = self.parameter_form()
        fetch, started, release = self.delayed_response(["old"])
        self.open_dict.side_effect = fetch
        submit()
        self.assertTrue(started.wait(timeout=5))
        stale, args = next(iter(self.gui.pending.values()))
        self.gui.close(dialog)
        self.assertFalse(self.gui.pending)
        self.assertIsNone(self.app.field_toplevel)
        entry.reset_mock()
        submit()
        entry.get.assert_not_called()
        self.assertEqual(len(self.gui.threads), 1)
        release.set()
        self.gui.finish_workers(self)
        stale(*args)
        dialog.destroy.assert_called_once()
        self.app.listbox_right.insert.assert_not_called()

    def test_destroy_dialog_directly_invalidates_ready_result(self):
        dialog, entry, submit = self.parameter_form()
        self.open_dict.return_value = ["old"]
        submit()
        self.gui.finish_workers(self)
        dialog.destroy()
        self.assertIsNone(self.app.field_toplevel)
        self.assertFalse(self.gui.pending)
        self.app.listbox_right.insert.assert_not_called()

    def test_selection_or_category_change_closes_pending_dialog(self):
        for change in ("selection", "category", "new search"):
            with self.subTest(change=change):
                dialog, entry, submit = self.parameter_form()
                fetch, started, release = self.delayed_response(["old"])
                self.open_dict.side_effect = fetch
                submit()
                self.assertTrue(started.wait(timeout=5))
                stale, args = next(iter(self.gui.pending.values()))
                if change == "selection":
                    self.app.listbox_left.curselection.return_value = (0,)
                    self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
                elif change == "category":
                    menus._select_menu(self.app, menus.menus_list["Taxes"])
                else:
                    self.open_dict.side_effect = None
                    self.open_dict.return_value = ["new"]
                    self.select("Todos os bancos")
                dialog.destroy.assert_called_once()
                self.assertIsNone(self.app.field_toplevel)
                release.set()
                self.gui.finish_workers(self)
                if change == "new search":
                    self.complete()
                self.assertFalse(self.gui.pending)
                self.app.listbox_right.reset_mock()
                stale(*args)
                self.app.listbox_right.insert.assert_not_called()

    def test_selection_change_before_submit_closes_unsubmitted_dialog(self):
        dialog, entry, submit = self.parameter_form()
        self.app.listbox_left.curselection.return_value = (0,)
        self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
        dialog.destroy.assert_called_once()
        submit()
        self.open_dict.assert_not_called()

    def test_parameter_text_selection_does_not_close_dialog_or_cancel_request(self):
        dialog, entry, submit = self.parameter_form()
        # Exporting an Entry's text selection can clear the Listbox's selection.
        self.app.listbox_left.curselection.return_value = ()
        self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
        self.assertIs(self.app.field_toplevel, dialog)
        dialog.destroy.assert_not_called()

        fetch, started, release = self.delayed_response(["current"])
        self.open_dict.side_effect = fetch
        submit()
        self.assertTrue(started.wait(timeout=5))
        self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
        self.assertEqual(len(self.gui.pending), 1)
        # Re-selecting the original operation still belongs to the same form.
        self.app.listbox_left.curselection.return_value = (1,)
        self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
        self.assertEqual(len(self.gui.pending), 1)
        dialog.destroy.assert_not_called()
        # An actual change of operation must still invalidate the pending query.
        self.app.listbox_left.curselection.return_value = (0,)
        self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
        self.assertFalse(self.gui.pending)
        dialog.destroy.assert_called_once()
        release.set()
        self.gui.finish_workers(self)
        self.app.listbox_right.insert.assert_not_called()

    def shutdown_parameter_query(self, external=False):
        dialog, entry, submit = self.parameter_form()
        fetch, started, release = self.delayed_response(["old"])
        self.open_dict.side_effect = fetch
        submit()
        self.assertTrue(started.wait(timeout=5))
        stale, args = next(iter(self.gui.pending.values()))
        if external:
            self.gui.window.destroy()
        else:
            self.gui.close()
        self.assertFalse(self.gui.pending)
        self.assertFalse(self.gui.live_dialogs)
        entry.reset_mock()
        submit()
        entry.get.assert_not_called()
        release.set()
        self.gui.finish_workers(self)
        stale(*args)
        dialog.destroy.assert_called_once()
        self.app.listbox_right.insert.assert_not_called()

    def test_application_shutdown_during_parameter_request_leaves_no_dialogs(self):
        self.shutdown_parameter_query()

    def test_external_root_destruction_during_parameter_request_leaves_no_dialogs(self):
        self.shutdown_parameter_query(external=True)
