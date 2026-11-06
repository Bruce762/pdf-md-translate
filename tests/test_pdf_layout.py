"""Opt-in browser regression: MD_TRANSLATOR_TEST_CHROME=1 python -m unittest discover -s tests."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from md_translator import convert_to_pdf


@unittest.skipUnless(os.environ.get("MD_TRANSLATOR_TEST_CHROME") == "1", "requires Chrome")
class PdfLayoutTests(unittest.TestCase):
    def test_waits_for_mathjax_beyond_the_old_ten_second_budget(self):
        from pypdf import PdfReader

        css = Path(convert_to_pdf.__file__).with_name("default.css").as_uri()
        with tempfile.TemporaryDirectory() as folder:
            html = Path(folder) / "delayed.html"
            pdf = Path(folder) / "delayed.pdf"
            html.write_text(f"""<!doctype html><html><head>
<link rel="stylesheet" href="{css}">
<script>
window.MathJax = {{startup: {{promise: new Promise(resolve => {{
    setTimeout(() => {{
        document.getElementById('formula').innerHTML =
            '<mjx-container><mjx-math style="display:inline-block;white-space:nowrap">' +
            '<span style="display:inline-block;width:100em">FORMULA_READY</span>' +
            'FORMULA_END</mjx-math></mjx-container>';
        resolve();
    }}, 12000);
}})}}}};
</script></head><body><p>BODY_SIZE_PROBE</p><div id="formula"></div></body></html>""", encoding="utf-8")
            self.assertTrue(convert_to_pdf.convert_html_to_pdf(str(html), str(pdf)))
            reader = PdfReader(pdf)
            sizes = []

            def visit(text, cm, tm, font, size):
                if "BODY_SIZE_PROBE" in text:
                    sizes.append(size * abs(cm[0]))

            text = "".join(page.extract_text(visitor_text=visit) for page in reader.pages)
            self.assertIn("FORMULA_READY", text)
            self.assertIn("FORMULA_END", text)
            self.assertEqual(len(sizes), 1)
            self.assertAlmostEqual(sizes[0], 14, delta=0.05)

    def test_missing_mathjax_preserves_the_existing_pdf(self):
        with tempfile.TemporaryDirectory() as folder:
            html = Path(folder) / "missing-math.html"
            pdf = Path(folder) / "existing.pdf"
            pdf.write_bytes(b"existing PDF")
            missing = (Path(folder) / "missing-mathjax.js").as_uri()
            html.write_text(f'<html><head><script src="{missing}"></script></head>'
                            '<body><span class="math">x+y</span></body></html>', encoding="utf-8")
            self.assertFalse(convert_to_pdf.convert_html_to_pdf(str(html), str(pdf)))
            self.assertEqual(pdf.read_bytes(), b"existing PDF")

    def test_wide_math_and_table_preserve_body_size_and_bundled_chinese_font(self):
        from pypdf import PdfReader

        css = Path(convert_to_pdf.__file__).with_name("default.css").as_uri()
        with tempfile.TemporaryDirectory() as folder:
            for wide in (False, True):
                with self.subTest(wide=wide):
                    # Model MathJax's font-relative CHTML layout without a CDN.
                    # A wide formula must shrink locally and retain its tail.
                    math = """
<mjx-container><mjx-math style="display:inline-block;white-space:nowrap">
<span style="display:inline-block;width:100em">FORMULA_START</span>FORMULA_END
</mjx-math></mjx-container>
""" if wide else ""
                    table = ("<table><tr>" + "".join(
                        "<td>" + "unbreakable" * 30 + "</td>" for _ in range(8)
                    ) + "</tr></table>") if wide else ""
                    html = f"""<!doctype html><html><head>
<link rel="stylesheet" href="{css}">
<script>window.MathJax = {{startup: {{promise: Promise.resolve()}}}};</script>
</head><body><h1>繁體中文標題</h1><p>BODY_SIZE_PROBE 中文字型測試 <strong>粗體文字</strong></p>{math}{table}
<p>AFTER_SIZE_PROBE</p></body></html>"""
                    pandoc = Mock()
                    pandoc.convert_file.return_value = html
                    source = Path(folder) / "input.md"
                    source.write_text("test", encoding="utf-8")
                    rendered_html = Path(folder) / "input.html"
                    pdf = Path(folder) / "output.pdf"
                    with patch.object(convert_to_pdf, "import_pypandoc", return_value=pandoc):
                        self.assertTrue(convert_to_pdf.convert_markdown_to_html(
                            str(source), str(rendered_html), str(Path(convert_to_pdf.__file__).with_name("default.css"))
                        ))
                    self.assertTrue(convert_to_pdf.convert_html_to_pdf(str(rendered_html), str(pdf)))
                    reader = PdfReader(pdf)
                    probes = []
                    fonts = set()
                    text = ""

                    def visit(value, cm, tm, font, size):
                        if "SIZE_PROBE" in value:
                            probes.append(size * abs(cm[0]))

                    for page in reader.pages:
                        text += page.extract_text(visitor_text=visit)
                        fonts.update(str(ref.get_object().get("/BaseFont")) for ref in
                                     page["/Resources"].get("/Font", {}).values())
                    self.assertEqual(len(probes), 2)
                    for size in probes:
                        self.assertAlmostEqual(size, 14, delta=0.05)
                    self.assertTrue(any("NotoSerifTC-Regular" in font for font in fonts), fonts)
                    self.assertTrue(any("NotoSerifTC-Bold" in font for font in fonts), fonts)
                    if wide:
                        self.assertIn("FORMULA_END", text)


if __name__ == "__main__":
    unittest.main()
