"""Layout contracts using simulated widgets only."""
import unittest
from unittest.mock import call

from app_test_support import AppHarness


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.gui = AppHarness()
        self.app = self.gui.app

    def test_root_prioritizes_results_and_expands_content(self):
        self.app.window.columnconfigure.assert_has_calls([
            call(0, weight=1), call(1, weight=3)])
        self.app.window.rowconfigure.assert_has_calls([
            call(0, weight=3), call(1, weight=1)])

    def test_panels_and_content_expand(self):
        for panel in (self.app.operations_frame, self.app.results_frame,
                      self.app.information_frame):
            self.assertEqual(panel.grid.call_args.kwargs['sticky'], 'nsew')
            panel.columnconfigure.assert_called_with(0, weight=1)
        self.app.operations_frame.rowconfigure.assert_called_with(2, weight=1)
        self.app.results_frame.rowconfigure.assert_called_with(1, weight=1)
        self.app.information_frame.rowconfigure.assert_called_with(0, weight=1)
        for widget in (self.app.listbox_left, self.app.listbox_right, self.app.text):
            self.assertEqual(widget.grid.call_args.kwargs['sticky'], 'nsew')

    def test_only_functional_query_button_remains(self):
        self.assertEqual(len(self.gui.buttons), 1)
        self.assertIs(self.gui.buttons[0], self.app.botao)
        self.assertEqual(self.gui.factories['Button'].call_args.kwargs['command'],
                         self.app.search)

    def test_scrollbars_connect_both_directions(self):
        calls = self.gui.factories['Scrollbar'].call_args_list
        self.assertEqual(len(calls), 4)
        self.assertEqual([item.kwargs['orient'] for item in calls],
                         ['vertical', 'vertical', 'horizontal', 'vertical'])
        self.assertEqual([item.kwargs['command'] for item in calls],
                         [self.app.listbox_left.yview, self.app.listbox_right.yview,
                          self.app.listbox_right.xview, self.app.text.yview])
        self.app.listbox_right.config.assert_any_call(
            xscrollcommand=self.app.results_x_scrollbar.set)
        self.app.results_x_scrollbar.grid.assert_called_once_with(
            row=2, column=0, sticky='ew')
        for widget in (self.app.listbox_left, self.app.listbox_right, self.app.text):
            self.assertTrue(any('yscrollcommand' in item.kwargs
                                for item in widget.config.call_args_list))

    def test_public_widgets_keep_their_panel_and_identity(self):
        self.assertEqual(self.gui.factories['Listbox'].call_args_list[0].args,
                         (self.app.operations_frame,))
        self.assertEqual(self.gui.factories['Listbox'].call_args_list[1].args,
                         (self.app.results_frame,))
        self.assertEqual(self.gui.factories['Text'].call_args.args,
                         (self.app.information_frame,))
        self.assertIs(self.app.entry, self.gui.entries[0])
        self.app.listbox_left.bind.assert_called_once_with(
            '<<ListboxSelect>>', self.app._on_operation_selected)
        self.assertEqual(self.gui.factories['Label'].call_count, 2)
