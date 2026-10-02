import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

# Filename and resource-lifetime tests do not require a real PDF parser.
sys.modules.setdefault('fitz', types.ModuleType('fitz'))
spec = importlib.util.spec_from_file_location('renamer', Path(__file__).parents[1] / 'rename_pdf_files.py')
renamer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renamer)


class FilenameTests(unittest.TestCase):
    def test_reserved_metadata_titles_can_be_created_on_windows(self):
        with tempfile.TemporaryDirectory() as folder:
            for title in ['CON', 'nul.txt', 'LPT1.paper', 'COM¹.title', 'AUX .draft']:
                cleaned = renamer.clean_filename(title)
                self.assertTrue(cleaned.startswith('_'), title)
                path = Path(folder) / (cleaned + '.pdf')
                path.write_bytes(b'filename fixture')
                self.assertTrue(path.is_file(), title)

    def test_controls_and_trailing_dots_are_removed_without_changing_normal_titles(self):
        self.assertEqual(renamer.clean_filename('Normal Paper'), 'Normal Paper')
        self.assertEqual(renamer.clean_filename('Normal\x00 Paper.  '), 'Normal Paper')
        self.assertEqual(renamer.clean_filename('  ...  '), 'Untitled Paper')

    def test_metadata_failure_closes_document(self):
        class Document:
            closed = False
            def __enter__(self): return self
            def __exit__(self, *args): self.closed = True
            @property
            def metadata(self): raise RuntimeError('fixture metadata failure')
        document = Document()
        with patch.object(renamer.fitz, 'open', return_value=document, create=True):
            self.assertIsNone(renamer.extract_title_from_metadata('fixture.pdf'))
        self.assertTrue(document.closed)


if __name__ == '__main__':
    unittest.main()
