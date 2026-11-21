
import csv
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "processed"

# Azure Blob Storage configuration
AZURE_CONTAINER_NAME = "sales-data"
AZURE_BLOB_NAME = "sales_data_combined.csv"

# Kolom yang harus tersedia dalam dataset
REQUIRED_COLUMNS = [
    "order_no",
    "order_date",
    "order_time",
    "order_source",
    "customer_id",
    "customer_type",
    "item_group",
    "item_name",
    "qty",
    "currency",
    "unit_price",
    "discount_amount",
    "amount",
    "total_cost",
    "profit",
    "payment_type",
    "order_status",
]


def validate_file(file_path):
    """Memvalidasi struktur file CSV."""

    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"File kosong atau tidak valid: {file_path.name}")

        missing_columns = [
            column for column in REQUIRED_COLUMNS
            if column not in reader.fieldnames
        ]

        if missing_columns:
            raise ValueError(
                f"Kolom tidak ditemukan pada {file_path.name}: "
                f"{missing_columns}"
            )

        rows = list(reader)

        if not rows:
            raise ValueError(f"Tidak terdapat data pada {file_path.name}")

        return rows


def upload_to_azure(file_path, blob_name):
    """Mengunggah file hasil ingestion ke Azure Blob Storage."""

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if not connection_string:
        raise ValueError(
            "Environment variable AZURE_STORAGE_CONNECTION_STRING "
            "belum tersedia."
        )

    # Import dilakukan di dalam fungsi agar unit testing validasi
    # tetap dapat berjalan tanpa koneksi Azure.
    from azure.storage.blob import BlobServiceClient

    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string
    )

    blob_client = blob_service_client.get_blob_client(
        container=AZURE_CONTAINER_NAME,
        blob=blob_name
    )

    with open(file_path, "rb") as file:
        blob_client.upload_blob(file, overwrite=True)

    print("\n=== AZURE UPLOAD ===")
    print(f"Container       : {AZURE_CONTAINER_NAME}")
    print(f"Blob name       : {blob_name}")
    print("Upload status   : SUCCESS")


def run_ingestion(upload_to_cloud=False):
    """Membaca, memvalidasi, dan menggabungkan seluruh dataset."""

    files = sorted(DATA_DIR.glob("sales_data_*.csv"))

    if not files:
        raise FileNotFoundError("Dataset CSV tidak ditemukan.")

    all_rows = []

    print("=== SALES DATA INGESTION ===")

    for file_path in files:
        rows = validate_file(file_path)

        all_rows.extend(rows)

        print(
            f"[SUCCESS] {file_path.name} | "
            f"{len(rows)} rows validated"
        )

    OUTPUT_DIR.mkdir(exist_ok=True)

    output_file = OUTPUT_DIR / "sales_data_combined.csv"

    with open(output_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=REQUIRED_COLUMNS
        )

        writer.writeheader()
        writer.writerows(all_rows)

    print("\n=== INGESTION SUMMARY ===")
    print(f"Total files       : {len(files)}")
    print(f"Total records     : {len(all_rows)}")
    print(f"Output file       : {output_file}")
    print(f"Execution time    : {datetime.now()}")

    # Upload hasil ingestion ke Azure jika diaktifkan
    if upload_to_cloud:
        upload_to_azure(
            file_path=output_file,
            blob_name=AZURE_BLOB_NAME
        )

    print("\nIngestion completed successfully!")


if __name__ == "__main__":
    run_ingestion(upload_to_cloud=True)
