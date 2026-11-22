import unittest
from unittest.mock import patch
from requests import Response
from requests.exceptions import HTTPError, Timeout, ConnectionError, JSONDecodeError
from app.App import query_error_message
import test_async_search


class ErrorMessagesTests(unittest.TestCase):
    def test_http_messages(self):
        for code, expected in [(400, 'Solicitação inválida'), (404, 'Recurso não encontrado'),
                               (429, 'Limite de requisições')] + [(c, 'Serviço temporariamente indisponível') for c in (500, 502, 503, 504)]:
            with self.subTest(code=code):
                response = Response()
                response.status_code = code
                self.assertIn(expected, query_error_message(HTTPError('technical', response=response)))

    def test_transport_json_and_unexpected_messages(self):
        for error, expected in [(Timeout(), 'Tempo limite'), (ConnectionError(), 'conectar à internet'),
                                (JSONDecodeError('bad', '', 0), 'JSON inválida'),
                                (RuntimeError('secret'), 'erro inesperado')]:
            with self.subTest(error=type(error)):
                self.assertIn(expected, query_error_message(error))
                self.assertNotIn('secret', query_error_message(error))


class FeedbackTests(test_async_search.AsyncSearchTests):
    def test_loading_completion_and_empty(self):
        for result in ([], {}, None, ['resultado']):
            with self.subTest(result=result):
                self.open_dict.return_value = result
                self.select()
                self.app.label_right.config.assert_called_with(text='Consultando...')
                self.complete()
                self.app.label_right.config.assert_called_with(
                    text='Consulta concluída.' if result else 'Nenhum resultado encontrado.')

    def test_waiting_cancel_and_stale_status(self):
        dialog, entry, submit, gates, activity, workers = self.saturated_parameter_requests()
        self.app.label_right.config.assert_called_with(text='Aguardando disponibilidade para consultar...')
        stale, args = next(iter(self.gui.pending.values()))
        self.gui.close(dialog)
        self.app.label_right.config.assert_called_with(text='Consulta cancelada.')
        self.app.label_right.reset_mock()
        for key in ('001', '002'):
            gates[key][1].set()
        self.gui.finish_workers(self)
        stale(*args)
        self.app.label_right.config.assert_not_called()

    def test_invalid_input_clears_previous_results_without_http(self):
        dialog, entry, submit = self.parameter_form('invalid')
        self.app.listbox_right.insert('end', 'old')
        self.app.listbox_right.delete.reset_mock()
        submit()
        self.app.listbox_right.delete.assert_called_with(0, 'end')
        self.open_dict.assert_not_called()


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite(loader.loadTestsFromTestCase(ErrorMessagesTests))
    for name in ('test_loading_completion_and_empty', 'test_waiting_cancel_and_stale_status', 'test_invalid_input_clears_previous_results_without_http'):
        suite.addTest(FeedbackTests(name))
    return suite
