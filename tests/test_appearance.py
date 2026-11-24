"""Main-window appearance contracts without real Tk or HTTP."""
import unittest
from app import configuration
from app_test_support import AppHarness


class AppearanceTests(unittest.TestCase):
    def setUp(self):
        self.gui = AppHarness()
        self.app = self.gui.app

    def options(self, name, index=-1):
        return self.gui.factories[name].call_args_list[index].kwargs

    def test_palette_is_centralized_and_legacy_dialog_colors_preserved(self):
        expected = dict(background='#111827', panel='#1F2937', surface='#0F172A',
                        text='#F3F4F6', secondary='#CBD5E1', accent='#60A5FA',
                        on_accent='#111827', border='#334155')
        for key, value in expected.items():
            self.assertEqual(configuration.colors[key], value)
        self.assertEqual(configuration.colors['grey'], '#1F2021')
        self.assertEqual(configuration.colors['white'], '#E5E4EA')
        self.assertIs(self.app.color, configuration.colors)

    def test_panels_and_root_use_palette(self):
        self.app.window.config.assert_called_with(bg=configuration.colors['background'])
        self.assertEqual(self.gui.factories['Frame'].call_count, 3)
        for item in self.gui.factories['Frame'].call_args_list:
            self.assertEqual(item.kwargs['bg'], configuration.colors['panel'])
            self.assertEqual(item.kwargs['highlightbackground'], configuration.colors['border'])

    def test_lists_have_readable_selection_and_focus(self):
        for index in (0, 1):
            options = self.options('Listbox', index)
            for option, color in (('bg', 'surface'), ('fg', 'text'),
                                  ('selectbackground', 'accent'),
                                  ('selectforeground', 'on_accent'),
                                  ('highlightcolor', 'accent')):
                self.assertEqual(options[option], configuration.colors[color])
            self.assertGreaterEqual(options['highlightthickness'], 1)
            self.assertEqual(options['bd'], 0)
            self.assertNotEqual(options['selectbackground'], options['selectforeground'])

    def test_fonts_are_centralized_and_results_are_monospace(self):
        fonts = configuration.fonts
        self.assertEqual(fonts['controls'], ('Segoe UI', 11))
        self.assertEqual(fonts['technical'], ('Consolas', 11))
        for widget, index, font in (('Entry', 0, 'controls'), ('Listbox', 0, 'controls'),
                                    ('Listbox', 1, 'technical'), ('Text', 0, 'technical'),
                                    ('Label', 0, 'title'), ('Label', 1, 'title'),
                                    ('Button', 0, 'controls')):
            self.assertEqual(self.options(widget, index)['font'], fonts[font])

    def test_button_is_highlighted_and_keeps_search_command(self):
        options = self.options('Button')
        self.assertEqual(options['text'], 'Consultar')
        self.assertEqual(options['command'], self.app.search)
        self.assertEqual(options['bg'], configuration.colors['accent'])
        self.assertEqual(options['fg'], configuration.colors['on_accent'])
        self.assertGreaterEqual(options['padx'], 12)
        self.assertGreaterEqual(options['pady'], 6)
        self.assertEqual(len(self.gui.buttons), 1)
        self.assertIs(self.app.botao, self.gui.buttons[0])

    def test_information_and_disabled_context_are_legible(self):
        options = self.options('Text')
        self.assertEqual(options['bg'], configuration.colors['surface'])
        self.assertEqual(options['fg'], configuration.colors['text'])
        self.assertEqual(options['insertbackground'], configuration.colors['text'])
        options = self.options('Entry')
        self.assertEqual(options['disabledbackground'], configuration.colors['panel'])
        self.assertEqual(options['disabledforeground'], configuration.colors['secondary'])
        self.assertEqual(options['state'], 'disabled')

    def test_all_scrollbars_share_visual_configuration(self):
        self.assertEqual(self.gui.factories['Scrollbar'].call_count, 4)
        for item in self.gui.factories['Scrollbar'].call_args_list:
            self.assertEqual(item.kwargs['bg'], configuration.colors['border'])
            self.assertEqual(item.kwargs['activebackground'], configuration.colors['accent'])
