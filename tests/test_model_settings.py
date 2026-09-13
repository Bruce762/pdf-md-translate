import contextlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

from md_translator.config import ConfigManager, DEFAULT_MODELS
from md_translator import main


class ModelSettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = patch('md_translator.config.Path.home', return_value=Path(self.temp.name))
        self.home.start()
        self.addCleanup(self.home.stop)
        self.manager = ConfigManager()
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def test_legacy_configuration_and_persistence(self):
        self.manager.config = {'openai_api_key': 'test-key', 'target_language': '日文'}
        self.assertEqual(self.manager.get_model('openai'), DEFAULT_MODELS['openai'])
        self.manager.set_model('openai', 'gpt-future-text')
        loaded = ConfigManager()
        self.assertEqual(loaded.get_model('openai'), 'gpt-future-text')
        self.assertEqual(loaded.config['target_language'], '日文')
        self.assertEqual(loaded.config['openai_api_key'], 'test-key')
        self.assertEqual(loaded.get_model('gemini'), DEFAULT_MODELS['gemini'])

    def test_invalid_model_does_not_change_settings(self):
        for value in ('', 'bad model', '\n'):
            with self.assertRaises(ValueError):
                self.manager.set_model('openai', value)
        self.assertEqual(self.manager.get_model('openai'), DEFAULT_MODELS['openai'])

    def test_live_list_filters_and_sorts(self):
        items = [SimpleNamespace(id=name, created=date) for name, date in
                 [('gpt-old', 10), ('gpt-image-2', 40), ('gpt-live-1', 50), ('gpt-future-text', 30), ('o3', 20)]]
        with patch.object(self.manager, 'get_openai_api_key', return_value='test-key'), patch('openai.OpenAI') as factory:
            factory.return_value.__enter__.return_value.models.list.return_value = items
            self.assertEqual([m.id for m in self.manager.list_openai_models()], ['gpt-future-text', 'o3', 'gpt-old'])

    def test_settings_menu_manual_model(self):
        with patch('builtins.input', side_effect=['3', '1', 'gpt-future-text', '3', '4']):
            self.manager._provider_submenu('openai')
        self.assertEqual(self.manager.get_model('openai'), 'gpt-future-text')

    def test_api_failure_keeps_old_selection(self):
        with patch.object(self.manager, 'list_openai_models', side_effect=RuntimeError('failure')), patch(
            'builtins.input', side_effect=['2', '3']
        ):
            self.manager._model_submenu('openai')
        self.assertEqual(self.manager.get_model('openai'), DEFAULT_MODELS['openai'])

    def test_live_selection_saved(self):
        with patch.object(self.manager, 'list_openai_models', return_value=[SimpleNamespace(id='gpt-future-text', created=10)]), patch(
            'builtins.input', side_effect=['2', '1', '3']
        ):
            self.manager._model_submenu('openai')
        self.assertEqual(ConfigManager().get_model('openai'), 'gpt-future-text')

    def test_translation_uses_saved_model_without_temperature(self):
        self.manager.config.update(openai_model='gpt-future-text', gemini_model='gemini-custom')
        with patch.object(main, 'config_manager', self.manager), patch.object(self.manager, 'get_openai_api_key', return_value='test-key'), patch.object(
            self.manager, 'get_gemini_api_key', return_value=''
        ), patch.object(main, 'OpenAI') as factory, patch.multiple(
            main, OPENAI_MODEL=main.OPENAI_MODEL, GEMINI_MODEL=main.GEMINI_MODEL,
            openai_client=main.openai_client, gemini_client=main.gemini_client,
            OPENAI_API_KEY='', GOOGLE_API_KEY='', API_PROVIDER='openai'
        ):
            main.init_api_config()
            factory.return_value.chat.completions.create.return_value.choices = [SimpleNamespace(message=SimpleNamespace(content='翻譯結果'))]
            self.assertEqual(main._call_openai_api('text', 'translate'), '翻譯結果')
            kwargs = factory.return_value.chat.completions.create.call_args.kwargs
            self.assertEqual(kwargs['model'], 'gpt-future-text')
            self.assertNotIn('temperature', kwargs)
            self.assertEqual(main.GEMINI_MODEL, 'gemini-custom')

    def test_reasoning_saved_per_model(self):
        self.manager.set_model('openai', 'gpt-6-astra')
        self.manager.set_reasoning_effort('max')
        self.manager.set_model('openai', 'gpt-5.4-mini')
        self.assertEqual(self.manager.get_reasoning_effort(), 'default')
        self.manager.set_reasoning_effort('none')
        loaded = ConfigManager()
        self.assertEqual(loaded.get_reasoning_effort('gpt-6-astra'), 'max')
        self.assertEqual(loaded.get_reasoning_effort(), 'none')

    def test_unsupported_efforts_and_unknown_models(self):
        for model, effort in [('gpt-6-astra', 'none'), ('gpt-5.4-mini', 'max'), ('gpt-future', 'high')]:
            self.manager.set_model('openai', model)
            with self.assertRaises(ValueError):
                self.manager.set_reasoning_effort(effort)
            self.assertEqual(self.manager.get_reasoning_effort(), 'default')

    def test_snapshot_efforts(self):
        self.manager.set_model('openai', 'gpt-6-astra-2026-09-01')
        self.manager.set_reasoning_effort('high')
        self.assertEqual(self.manager.get_reasoning_effort(), 'high')

    def test_reasoning_menu(self):
        self.manager.set_model('openai', 'gpt-6-astra')
        with patch('builtins.input', side_effect=['5', '2', '4']):
            self.manager._provider_submenu('openai')
        self.assertEqual(self.manager.get_reasoning_effort(), 'low')

    def test_reasoning_request_parameter_and_default_omission(self):
        self.manager.set_model('openai', 'gpt-6-astra')
        client = Mock()
        client.chat.completions.create.return_value.choices = [SimpleNamespace(message=SimpleNamespace(content='翻譯'))]
        with patch.object(main, 'config_manager', self.manager), patch.object(main, 'OPENAI_MODEL', 'gpt-6-astra'), patch.object(main, 'openai_client', client):
            for effort in ('high', 'default'):
                self.manager.set_reasoning_effort(effort)
                main._call_openai_api('text', 'translate')
                kwargs = client.chat.completions.create.call_args.kwargs
                if effort == 'default':
                    self.assertNotIn('reasoning_effort', kwargs)
                else:
                    self.assertEqual(kwargs['reasoning_effort'], effort)

    def test_invalid_saved_effort_not_sent(self):
        self.manager.config['openai_reasoning_efforts'] = {'gpt-6-astra': 'none'}
        self.assertEqual(self.manager.get_reasoning_effort('gpt-6-astra'), 'default')
