import contextlib
import io
import os
from pathlib import Path
import tempfile
import subprocess
import unittest
from unittest.mock import patch, Mock

from md_translator import main
from md_translator import convert_to_pdf


class PdfFailureTests(unittest.TestCase):
    def test_completed_pdf_stops_chrome_without_waiting_for_exit(self):
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / "output.pdf"
            pdf.write_bytes(b"finished PDF")
            process = Mock()
            process.poll.return_value = None
            with patch.object(convert_to_pdf.subprocess, "Popen", return_value=process), patch.object(
                convert_to_pdf, "_pdf_is_complete", return_value=True
            ), patch.object(convert_to_pdf.time, "monotonic", side_effect=[0, 0, 0, 0, 2, 2]), patch.object(
                convert_to_pdf.time, "sleep"
            ):
                self.assertTrue(convert_to_pdf._print_with_chrome(["chrome"], str(pdf)))
            process.terminate.assert_called_once()
            process.wait.assert_called_once_with(timeout=3)

    def test_incomplete_pdf_times_out_and_stops_chrome(self):
        process = Mock()
        process.poll.return_value = None
        with patch.object(convert_to_pdf.subprocess, "Popen", return_value=process), patch.object(
            convert_to_pdf.time, "monotonic", side_effect=[0, 0, 121]
        ):
            self.assertFalse(convert_to_pdf._print_with_chrome(["chrome"], "missing.pdf"))
        process.terminate.assert_called_once()

    def test_incomplete_trailer_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / "partial.pdf"
            pdf.write_bytes(b"%PDF-1.7 incomplete")
            self.assertFalse(convert_to_pdf._pdf_is_complete(str(pdf)))

    def test_chrome_without_output_does_not_replace_existing_pdf(self):
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / "output.pdf"
            pdf.write_bytes(b"existing PDF")
            with patch.object(convert_to_pdf, "get_chrome_path", return_value="chrome"), patch.object(
                convert_to_pdf, "_print_with_chrome", return_value=False
            ):
                self.assertFalse(convert_to_pdf.convert_html_to_pdf("input.html", str(pdf)))
            self.assertEqual(pdf.read_bytes(), b"existing PDF")

    def test_failure_preserves_markdown_and_images(self):
        for pdf_input in (True, False):
            with self.subTest(pdf_input=pdf_input), tempfile.TemporaryDirectory() as folder:
                previous = os.getcwd()
                self.addCleanup(os.chdir, previous)
                os.chdir(folder)
                original = Path("paper.md")
                translated = Path("paper_trans.md")
                image = Path("images/paper/figure.png")
                original.write_text("original")
                translated.write_text("translated")
                image.parent.mkdir(parents=True)
                image.write_bytes(b"image")
                output = io.StringIO()
                with patch.object(main, "translate_markdown"), patch.object(
                    main, "convert_pdf_with_mineru", return_value=str(original)
                ), patch.object(main, "_convert_translated_to_pdf", return_value=False), contextlib.redirect_stdout(output):
                    with self.assertRaises(SystemExit) as error:
                        if pdf_input:
                            main._handle_pdf_file("paper.pdf", "繁體中文")
                        else:
                            main._handle_md_file(str(original), "繁體中文")
                self.assertEqual(error.exception.code, 1)
                self.assertEqual(original.read_text(), "original")
                self.assertEqual(translated.read_text(), "translated")
                self.assertEqual(image.read_bytes(), b"image")
                self.assertNotIn("✅ 完成！", output.getvalue())
                os.chdir(previous)
