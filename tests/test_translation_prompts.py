import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from md_translator.config import ConfigManager
from md_translator.prompts import build_translation_prompts
from md_translator import main


class TranslationPromptTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        home = patch('md_translator.config.Path.home', return_value=Path(temp.name))
        home.start()
        self.addCleanup(home.stop)
        self.manager = ConfigManager()
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)

    def test_legacy_defaults_and_original_prompt(self):
        self.manager.config = {'target_language': '日文'}
        self.assertEqual(self.manager.get_translation_prompt_style(), 'academic')
        prompt, system = build_translation_prompts('source', '日文', True)
        self.assertTrue(system.startswith('你的專長是學術論文翻譯。'))
        self.assertIn('專業的日文', system)
        self.assertIn('範例輸入', prompt)
        self.assertIn('6. 刪除所有標題編號', system)

    def test_setup_selection_persists_and_preserves_other_settings(self):
        self.manager.config['openai_model'] = 'existing-model'
        with patch('builtins.input', side_effect=['3', '2', '4']):
            self.manager.reconfigure()
        loaded = ConfigManager()
        self.assertEqual(loaded.get_translation_prompt_style(), 'plain')
        self.assertEqual(loaded.get_model('openai'), 'existing-model')

    def test_custom_multiline_and_switching_back(self):
        with patch('builtins.input', side_effect=['3', '翻譯成 {target_language}', '使用短句。', '.']):
            self.manager._translation_prompt_submenu()
        loaded = ConfigManager()
        self.assertEqual(loaded.get_custom_translation_prompt(), '翻譯成 {target_language}\n使用短句。')
        loaded.set_translation_prompt('academic')
        with patch('builtins.input', side_effect=['3', '.']):
            loaded._translation_prompt_submenu()
        self.assertEqual(ConfigManager().get_translation_prompt_style(), 'custom')

    def test_cancel_invalid_empty_and_interrupted_input(self):
        self.manager.set_translation_prompt('plain')
        for answers in ([''], ['9'], ['3', '.'], ['3', 'partial', EOFError()], ['3', KeyboardInterrupt()]):
            with patch('builtins.input', side_effect=answers):
                self.manager._translation_prompt_submenu()
            self.assertEqual(ConfigManager().get_translation_prompt_style(), 'plain')
        with self.assertRaises(ValueError):
            self.manager.set_translation_prompt('custom', ' ')
        with self.assertRaises(ValueError):
            self.manager.set_translation_prompt('unknown')
        self.assertEqual(ConfigManager().get_translation_prompt_style(), 'plain')

    def test_first_setup_offers_prompt_selection(self):
        with patch('builtins.input', side_effect=['1', '', '2']):
            self.manager.setup_wizard()
        self.assertEqual(ConfigManager().get_translation_prompt_style(), 'plain')

    def test_both_providers_receive_selected_prompt(self):
        for provider, adapter in [('openai', '_call_openai_api'), ('gemini', '_call_gemini_api')]:
            for style in ('academic', 'plain', 'custom'):
                self.manager.config['api_provider'] = provider
                self.manager.set_translation_prompt(style, '採用短句，翻成 {target_language}；保留 {other}。')
                with patch.object(main, 'config_manager', self.manager), patch.object(main, adapter, return_value='譯文') as call:
                    self.assertEqual(main.call_translation_api('source $x$', True, '英文'), '譯文')
                prompt, system = call.call_args.args
                self.assertIn('source $x$', prompt)
                self.assertIn('英文', system)
                self.assertIn('LaTeX', system)
                self.assertIn('刪除所有標題編號', system)
                if style == 'academic':
                    self.assertIn('範例輸入', prompt)
                else:
                    self.assertNotIn('範例輸入', prompt)
                if style == 'plain':
                    self.assertIn('目的是讓讀者看懂', system)
                    self.assertIn('不省略內容', system)
                if style == 'custom':
                    self.assertIn('採用短句，翻成 英文；保留 {other}。', system)
                    self.assertNotIn('範例輸出', prompt)

    def test_empty_saved_custom_falls_back_to_default(self):
        self.manager.config.update(translation_prompt_style='custom', custom_translation_prompt='')
        self.assertEqual(self.manager.get_translation_prompt_style(), 'academic')
