
import unittest
import csv
import tempfile
from pathlib import Path

import sys

# Menambahkan folder src ke Python path
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from ingestion import validate_file, REQUIRED_COLUMNS


class TestDataIngestion(unittest.TestCase):

    def test_valid_csv_file(self):
        """Memastikan file CSV dengan kolom lengkap dapat dibaca."""

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "valid_data.csv"

            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=REQUIRED_COLUMNS
                )

                writer.writeheader()

                writer.writerow({
                    column: "test_value"
                    for column in REQUIRED_COLUMNS
                })

            rows = validate_file(file_path)

            self.assertEqual(len(rows), 1)
            self.assertEqual(
                list(rows[0].keys()),
                REQUIRED_COLUMNS
            )

    def test_missing_columns(self):
        """Memastikan file dengan kolom tidak lengkap menghasilkan error."""

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "invalid_data.csv"

            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                writer.writerow(["order_no", "order_date"])
                writer.writerow(["ORD001", "2026-04-01"])

            with self.assertRaises(ValueError):
                validate_file(file_path)

    def test_empty_csv_file(self):
        """Memastikan file CSV tanpa data menghasilkan error."""

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "empty_data.csv"

            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=REQUIRED_COLUMNS
                )

                writer.writeheader()

            with self.assertRaises(ValueError):
                validate_file(file_path)


if __name__ == "__main__":
    unittest.main()
