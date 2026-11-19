import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_project import check_project, parse_rules


TABLE = """| ID | 证据 | PDF页 | 规范或观察 |
| --- | --- | --- | --- |
| X01 | 明确 | 1 | 第一个来源页的明确条目。 |
| X02 | 样例 | 2 | 第二个来源页的观察条目。 |
"""


class SourceCoverageTests(unittest.TestCase):
    def test_actual_project(self):
        result = check_project(ROOT)
        self.assertEqual(result["source_pages"], 17)
        self.assertTrue(result["source_pdf_sha256_verified"])
        self.assertFalse(result["thesis_file_checked"])

    def test_changed_source_pdf_rejected(self):
        content = (ROOT / "skills/nnu-thesis-style-2026/references/source.pdf").read_bytes()
        changed = bytes([content[0] ^ 1]) + content[1:]
        with patch("check_project.Path.read_bytes", return_value=changed):
            with self.assertRaisesRegex(ValueError, "source PDF SHA256 mismatch"):
                check_project(ROOT)

    def test_truncated_source_pdf_rejected(self):
        with patch("check_project.Path.read_bytes", return_value=b""):
            with self.assertRaisesRegex(ValueError, "source PDF size mismatch"):
                check_project(ROOT)

    def test_valid_table(self):
        rules = parse_rules(TABLE, 2)
        self.assertEqual([rule["evidence"] for rule in rules], ["明确", "样例"])

    def test_duplicate_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate rule ID"):
            parse_rules(TABLE.replace("X02", "X01"), 2)

    def test_unsupported_evidence_rejected(self):
        with self.assertRaisesRegex(ValueError, "evidence label"):
            parse_rules(TABLE.replace("样例", "推测"), 2)

    def test_out_of_range_page_rejected(self):
        with self.assertRaisesRegex(ValueError, "out-of-range"):
            parse_rules(TABLE.replace("| 2 |", "| 3 |"), 2)

    def test_missing_page_rejected(self):
        with self.assertRaisesRegex(ValueError, "not covered"):
            parse_rules(TABLE.replace("| 2 |", "| 1 |"), 2)

    def test_duplicate_source_page_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate or out-of-range"):
            parse_rules(TABLE.replace("| 2 |", "| 1,2,2 |"), 2)

    def test_empty_statement_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty statement"):
            parse_rules(TABLE.replace("第二个来源页的观察条目。", ""), 2)

    def test_malformed_columns_rejected(self):
        with self.assertRaisesRegex(ValueError, "four rule columns"):
            parse_rules(TABLE.replace("第二个来源页的观察条目。", "多余 | 列"), 2)

    def test_no_rules_rejected(self):
        with self.assertRaisesRegex(ValueError, "no source rules"):
            parse_rules("# empty", 2)


if __name__ == "__main__":
    unittest.main()
