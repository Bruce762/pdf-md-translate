import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from md_translator import main


class MineruCommandTests(unittest.TestCase):
    def _run_conversion(self, use_cpu):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "paper.pdf"
            source.write_bytes(b"%PDF-1.7")
            output = root / "output"

            def fake_run(command, **kwargs):
                backend_dir = "auto" if use_cpu else "hybrid_auto"
                temp_output = Path(command[command.index("-o") + 1])
                markdown = temp_output / source.stem / backend_dir / f"{source.stem}.md"
                markdown.parent.mkdir(parents=True)
                markdown.write_text("converted", encoding="utf-8")

                class Result:
                    returncode = 0

                return Result()

            with patch.object(main.subprocess, "run", side_effect=fake_run) as runner, contextlib.redirect_stdout(io.StringIO()):
                result = main.convert_pdf_with_mineru(str(source), str(output), use_cpu=use_cpu)

            self.assertEqual(Path(result).read_text(encoding="utf-8"), "converted")
            return runner.call_args.args[0]

    def test_hybrid_uses_default_medium_effort(self):
        command = self._run_conversion(use_cpu=False)
        self.assertIn(
            ["-b", "hybrid-engine"],
            [command[index:index + 2] for index in range(len(command) - 1)],
        )
        self.assertNotIn("--effort", command)

    def test_pipeline_does_not_receive_effort(self):
        command = self._run_conversion(use_cpu=True)
        self.assertIn(
            ["-b", "pipeline"],
            [command[index:index + 2] for index in range(len(command) - 1)],
        )
        self.assertNotIn("--effort", command)


if __name__ == "__main__":
    unittest.main()
