"""Deterministic incremental display tests: no real Tk, network or sleeps."""

import unittest
from tkinter import TclError
from unittest.mock import call, patch

from app import menus
import test_async_search


class IncrementalDisplayTests(test_async_search.AsyncSearchTests):
    def setUp(self):
        super().setUp()
        self.clock = patch("app.App.perf_counter", return_value=0)
        self.timer = self.clock.start()
        self.addCleanup(self.clock.stop)

    def start_display(self, result=None, parameterized=False):
        self.open_dict.return_value = list(range(1000)) if result is None else result
        if parameterized:
            dialog, entry, submit = self.parameter_form()
            submit()
        else:
            self.select()
        self.gui.finish_workers(self)
        self.gui.run_next()
        return next(iter(self.gui.pending.values()), None)

    def drain_display(self):
        for _ in range(1000):
            if not self.gui.pending:
                return
            self.assertEqual(len(self.gui.pending), 1)
            before = self.app.listbox_right.insert.call_count
            self.gui.run_next()
            self.assertLessEqual(self.app.listbox_right.insert.call_count - before, 100)
        self.fail("Display did not finish")

    def assert_stale_is_inert(self, stale):
        self.assertIsNotNone(stale, "Expected a partially displayed result")
        self.app.listbox_right.reset_mock()
        self.app.label_right.reset_mock()
        before = dict(self.gui.pending)
        callback, args = stale
        callback(*args)
        self.app.listbox_right.insert.assert_not_called()
        self.app.label_right.config.assert_not_called()
        self.assertEqual(self.gui.pending, before)

    def test_ten_thousand_records_batched_in_both_query_paths(self):
        result = [{"id": n, "nome": "São Luís"} for n in range(10000)]
        expected = [call("end", line) for n in range(10000)
                    for line in (f"{n + 1}.", f"  id: {n}", "  nome: São Luís")]
        for parameterized in (False, True):
            with self.subTest(parameterized=parameterized):
                self.app.listbox_right.reset_mock()
                self.app.label_right.reset_mock()
                worker_count = len(self.gui.threads)
                self.start_display(result, parameterized)
                self.assertEqual(self.app.listbox_right.insert.call_count, 100)
                self.assertEqual(len(self.gui.pending), 1)
                self.app.label_right.config.assert_called_with(text="Exibindo resultados...")
                self.assertNotIn(call(text="Consulta concluída."),
                                 self.app.label_right.config.call_args_list)
                self.assertFalse(self.gui.live_dialogs)
                self.drain_display()
                self.assertEqual(self.app.listbox_right.insert.call_args_list, expected)
                self.app.label_right.config.assert_called_with(text="Consulta concluída.")
                self.assertEqual(len(self.gui.threads), worker_count + 1)

    def test_another_callback_runs_between_batches(self):
        self.start_display()
        observed = []
        self.gui.window.after(0, lambda: observed.append(self.app.listbox_right.insert.call_count))
        self.gui.run_next()
        self.gui.run_next()
        self.assertEqual(observed, [200])
        self.assertEqual(len(self.gui.pending), 1)
        self.drain_display()
        self.assertEqual(self.app.listbox_right.insert.call_count, 1000)

    def test_formatter_consumption_is_bounded_by_display_batch(self):
        visited = []

        class ObservedList(list):
            def __iter__(self):
                for item in super().__iter__():
                    visited.append(item)
                    yield item

        self.start_display(ObservedList(range(10000)))
        self.assertEqual(visited, list(range(100)))
        self.gui.run_next()
        self.assertEqual(visited, list(range(200)))
        self.app._invalidate_query()
        self.assertEqual(visited, list(range(200)))

    def test_time_budget_includes_formatting_and_widget_insertion(self):
        for expensive in ("format", "insert"):
            with self.subTest(expensive=expensive):
                elapsed = [0.0]
                self.timer.side_effect = lambda: elapsed[0]

                class CostlyList(list):
                    def __iter__(self):
                        for item in super().__iter__():
                            if expensive == "format":
                                elapsed[0] += 0.010
                            yield item

                def insert(*args):
                    if expensive == "insert":
                        elapsed[0] += 0.010

                self.app.listbox_right.reset_mock()
                self.app.listbox_right.insert.side_effect = insert
                self.start_display(CostlyList(range(250)))
                self.assertEqual(self.app.listbox_right.insert.call_count, 1)
                self.assertEqual(len(self.gui.pending), 1)
                self.gui.run_next()
                self.assertEqual(self.app.listbox_right.insert.call_count, 2)
                self.app._invalidate_query()

    def test_cancel_partial_display_and_ignore_already_dequeued_callback(self):
        stale = self.start_display()
        self.app._invalidate_query()
        self.assertFalse(self.gui.pending)
        self.app.label_right.config.assert_called_with(text="Consulta cancelada.")
        self.assert_stale_is_inert(stale)

    def test_new_query_cannot_receive_old_lines_or_status(self):
        stale = self.start_display()
        fetch, started, release = self.delayed_response(["novo"])
        self.open_dict.side_effect = fetch
        self.select()
        self.assertTrue(started.wait(timeout=5))
        self.app.label_right.config.assert_called_with(text="Consultando...")
        self.assert_stale_is_inert(stale)
        release.set()
        self.complete()
        self.app.listbox_right.insert.assert_called_once_with("end", "1. novo")
        self.app.label_right.config.assert_called_with(text="Consulta concluída.")

    def test_category_change_cancels_even_when_returning(self):
        stale = self.start_display()
        menus._select_menu(self.app, menus.menus_list["Taxes"])
        menus._select_menu(self.app, menus.menus_list["Bank/Stockbroker"])
        self.assertFalse(self.gui.pending)
        self.assert_stale_is_inert(stale)

    def test_operation_change_cancels_but_same_selection_does_not(self):
        stale = self.start_display()
        self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
        self.assertEqual(len(self.gui.pending), 1)
        self.app.listbox_left.curselection.return_value = (1,)
        self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
        self.assertFalse(self.gui.pending)
        self.assert_stale_is_inert(stale)

    def test_selecting_output_does_not_cancel_partial_display(self):
        for parameterized in (False, True):
            with self.subTest(parameterized=parameterized):
                self.app.listbox_right.reset_mock()
                self.start_display(list(range(250)), parameterized)
                self.app.listbox_left.curselection.return_value = ()
                self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
                self.assertEqual(len(self.gui.pending), 1)
                self.app.label_right.config.assert_called_with(text="Exibindo resultados...")
                self.drain_display()
                self.assertEqual(self.app.listbox_right.insert.call_args_list,
                                 [call("end", f"{n + 1}. {n}") for n in range(250)])

    def test_parameter_selection_snapshot_survives_normal_dialog_close(self):
        self.open_dict.return_value = list(range(250))
        dialog, entry, submit = self.parameter_form()
        self.app.listbox_left.curselection.return_value = ()
        submit()
        self.gui.finish_workers(self)
        self.gui.run_next()
        dialog.destroy.assert_called_once()
        self.assertEqual(len(self.gui.pending), 1)
        self.app.listbox_left.curselection.return_value = (1,)
        self.gui.emit(self.app.listbox_left, "<<ListboxSelect>>")
        self.drain_display()
        self.assertEqual(self.app.listbox_right.insert.call_count, 250)

    def test_new_result_replaces_partial_display_and_old_callback(self):
        stale = self.start_display()
        self.app.listbox_right.delete.reset_mock()
        self.app._show_result(list(range(250)))
        self.app.listbox_right.delete.assert_called_once_with(0, "end")
        self.assertEqual(len(self.gui.pending), 1)
        self.assert_stale_is_inert(stale)
        self.drain_display()
        self.assertEqual(self.app.listbox_right.insert.call_count, 150)
        self.app.label_right.config.assert_called_with(text="Consulta concluída.")

    def test_close_with_pending_display_never_touches_destroyed_widgets(self):
        stale = self.start_display()
        self.gui.close()
        self.assertTrue(self.gui.destroyed)
        self.assertFalse(self.gui.pending)
        self.assert_stale_is_inert(stale)
        self.app._show_result(["late"])
        self.app.listbox_right.insert.assert_not_called()
        self.app.label_right.config.assert_not_called()

    def test_external_destruction_cancels_display(self):
        stale = self.start_display()
        self.gui.window.destroy()
        self.assertFalse(self.gui.pending)
        self.assert_stale_is_inert(stale)

    def test_cancel_handles_tcl_error_and_stale_callback(self):
        stale = self.start_display()
        self.gui.window.after_cancel.side_effect = TclError("root is being destroyed")
        self.gui.close()
        self.assert_stale_is_inert(stale)

    def test_empty_zero_and_boolean_status_in_both_paths(self):
        for result, status in [(None, "Nenhum resultado encontrado."),
                               ([], "Nenhum resultado encontrado."),
                               ({}, "Nenhum resultado encontrado."),
                               ("", "Nenhum resultado encontrado."),
                               (0, "Consulta concluída."),
                               (False, "Consulta concluída."),
                               (True, "Consulta concluída.")]:
            for parameterized in (False, True):
                with self.subTest(result=result, parameterized=parameterized):
                    self.open_dict.return_value = result
                    if parameterized:
                        dialog, entry, submit = self.parameter_form()
                        submit()
                    else:
                        self.select()
                    self.complete()
                    self.app.label_right.config.assert_called_with(text=status)

    def test_rendering_does_not_change_two_workers_and_latest_pending_limit(self):
        stale = self.start_display()
        self.open_dict.reset_mock()
        dialog, entry, submit, gates, activity, workers = self.saturated_parameter_requests()
        self.assert_stale_is_inert(stale)
        self.assertEqual(activity["peak"], 2)
        entry.get.return_value = "004"
        submit()
        self.assertEqual(len(self.gui.threads), 3)  # One completed plus two active.
        gates["001"][1].set()
        self.finish_worker(workers[0])
        self.gui.run_next()
        self.assertTrue(gates["004"][0].wait(timeout=5))
        self.assertFalse(gates["003"][0].is_set())
        gates["004"][1].set()
        self.finish_worker(self.gui.threads[-1])
        self.gui.run_next()
        self.app.listbox_right.insert.assert_called_once_with("end", "1. 004")
        gates["002"][1].set()
        self.gui.finish_workers(self)
        self.assertEqual(activity["peak"], 2)
        self.assertFalse(self.gui.pending)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(IncrementalDisplayTests(name)
                              for name in IncrementalDisplayTests.__dict__
                              if name.startswith("test_"))
