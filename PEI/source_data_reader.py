from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Dict

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "SourceData"
SUPPORTED_EXTENSIONS = {".csv", ".json", ".xls", ".xlsx"}

# Optional schema checks for known PEI source files.
REQUIRED_COLUMNS = {
    "customer": {"Customer_ID", "First", "Last", "Age", "Country"},
    "order": {"Order_ID", "Item", "Amount", "Customer_ID"},
    "shipping": {"Shipping_ID", "Status", "Customer_ID"},
}

# Backward-compatible aliases used by the rest of the PEI framework.
DEFAULT_ALIAS_MAP = {
    "customer": "customers",
    "order": "orders",
    "shipping": "shipping",
}


def normalize_dataframe_name(file_path: Path) -> str:
    """Create a dictionary key from the file name without its extension."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", file_path.stem.strip().lower())
    return normalized.strip("_")


def excel_engine(file_path: Path) -> str | None:
    """Return the pandas engine for the supplied Excel extension."""
    if file_path.suffix.lower() == ".xls":
        return "xlrd"
    if file_path.suffix.lower() == ".xlsx":
        return "openpyxl"
    return None


def read_excel_file(file_path: Path) -> pd.DataFrame:
    """Read an Excel file using the correct pandas engine."""
    return pd.read_excel(file_path, engine=excel_engine(file_path))


def read_csv_file(file_path: Path) -> pd.DataFrame:
    """Read a CSV file."""
    return pd.read_csv(file_path)


def read_json_file(file_path: Path) -> pd.DataFrame:
    """Read a JSON file."""
    return pd.read_json(file_path)


FILE_READERS: dict[str, Callable[[Path], pd.DataFrame]] = {
    ".csv": read_csv_file,
    ".json": read_json_file,
    ".xls": read_excel_file,
    ".xlsx": read_excel_file,
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names for downstream ETL use."""
    standardized = df.copy()
    standardized.columns = [column.strip() for column in standardized.columns]
    return standardized


def supported_source_files(source_dir: Path = SOURCE_DIR) -> list[Path]:
    """Return all supported source files from SourceData."""
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    files = [
        file_path
        for file_path in sorted(source_dir.iterdir())
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not files:
        raise FileNotFoundError(f"No supported source files found in {source_dir}")
    return files


def read_source_file(file_path: Path) -> pd.DataFrame:
    """Read one supported source file into a pandas DataFrame."""
    suffix = file_path.suffix.lower()
    if suffix not in FILE_READERS:
        raise ValueError(f"Unsupported file type: {file_path.name}")
    return standardize_columns(FILE_READERS[suffix](file_path))


def validate_required_columns(
    dataframes: Dict[str, pd.DataFrame], required_columns_map: Dict[str, set[str]]
) -> None:
    """Raise an error when a known source file is missing required columns."""
    for source_name, required_columns in required_columns_map.items():
        if source_name not in dataframes:
            continue
        missing_columns = required_columns - set(dataframes[source_name].columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Missing required columns in {source_name}: {missing}")


def read_source_directory(
    source_dir: Path = SOURCE_DIR,
    required_columns_map: Dict[str, set[str]] | None = None,
) -> Dict[str, pd.DataFrame]:
    """
    Read all supported files from SourceData and return DataFrames keyed by file name.

    Example output keys for the current PEI project:
    - Customer.xls  -> customer
    - Order.csv     -> order
    - Shipping.json -> shipping
    """
    dataframes = {}
    duplicate_names = set()

    for file_path in supported_source_files(source_dir):
        dataframe_name = normalize_dataframe_name(file_path)
        if dataframe_name in dataframes:
            duplicate_names.add(dataframe_name)
            continue
        dataframes[dataframe_name] = read_source_file(file_path)

    if duplicate_names:
        duplicates = ", ".join(sorted(duplicate_names))
        raise ValueError(f"Duplicate dataframe names derived from file names: {duplicates}")

    if required_columns_map:
        validate_required_columns(dataframes, required_columns_map)
    return dataframes


def alias_dataframes(
    dataframes: Dict[str, pd.DataFrame], alias_map: Dict[str, str] | None = None
) -> Dict[str, pd.DataFrame]:
    """Rename dataframe keys when a framework-specific alias is needed."""
    aliases = alias_map or DEFAULT_ALIAS_MAP
    aliased = {}
    for source_name, df in dataframes.items():
        aliased[aliases.get(source_name, source_name)] = df
    return aliased


def read_sales_sources(source_dir: Path = SOURCE_DIR) -> Dict[str, pd.DataFrame]:
    """
    Backward-compatible wrapper for existing PEI scripts.

    Returns:
    - customers
    - orders
    - shipping
    """
    return alias_dataframes(read_source_directory(source_dir, required_columns_map=REQUIRED_COLUMNS))


def preview_dataframes(dataframes: Dict[str, pd.DataFrame]) -> None:
    """Print a small data preview and schema summary for each source."""
    for source_name, df in dataframes.items():
        print(f"\nSource: {source_name}")
        print(f"Rows: {len(df)} | Columns: {list(df.columns)}")
        print(df.head(5).to_string(index=False))


def main() -> None:
    dataframes = read_source_directory()
    preview_dataframes(dataframes)


if __name__ == "__main__":
    main()
