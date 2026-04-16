import argparse
import sqlite3
from pathlib import Path
from typing import Iterable

import pandas as pd

DB_PATH = Path("data/nv_knowledge.db")
TABLE_NAME = "nv_configs"


def normalize_columns(columns: Iterable[str]) -> list[str]:
    """Normalize messy Excel headers to stable snake_case names."""
    normalized = []
    for col in columns:
        c = str(col).strip().lower()
        c = c.replace("\\", "_").replace("/", "_").replace(" ", "_")
        c = c.replace("-", "_").replace(".", "_")
        while "__" in c:
            c = c.replace("__", "_")
        normalized.append(c)
    return normalized


def load_excel(excel_path: Path) -> pd.DataFrame:
    """Read all sheets and merge into a single dataframe."""
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    all_sheets = pd.read_excel(excel_path, sheet_name=None)
    frames = []

    for sheet_name, df in all_sheets.items():
        if df.empty:
            continue
        df = df.copy()
        df.columns = normalize_columns(df.columns)
        df["sheet_name"] = sheet_name
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    merged = pd.concat(frames, ignore_index=True)

    # Common aliases to improve compatibility with different Excel structures.
    alias_map = {
        "path": ["nv_path", "config_path", "parameter_path", "key"],
        "value": ["default_value", "val", "config_value"],
        "meaning": ["desc", "description", "comment", "含义", "说明"],
        "module": ["category", "group", "type"],
    }

    for target, aliases in alias_map.items():
        if target in merged.columns:
            continue
        for alias in aliases:
            if alias in merged.columns:
                merged[target] = merged[alias]
                break

    for required in ["path", "value", "meaning", "module"]:
        if required not in merged.columns:
            merged[required] = ""

    merged = merged.fillna("")
    return merged


def save_to_repository(df: pd.DataFrame, db_path: Path = DB_PATH) -> None:
    """Persist parsed data into SQLite + CSV for long-term repository usage."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path = db_path.parent / "nv_knowledge.csv"

    with sqlite3.connect(db_path) as conn:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")


def query_nv(keyword: str, db_path: Path = DB_PATH, limit: int = 100) -> pd.DataFrame:
    """Keyword query across path/value/meaning/module columns."""
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found: {db_path}. Please run import first."
        )

    sql = f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE path LIKE ? OR value LIKE ? OR meaning LIKE ? OR module LIKE ?
    LIMIT ?
    """
    pattern = f"%{keyword}%"

    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(sql, conn, params=[pattern, pattern, pattern, pattern, limit])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import modem APN/NV Excel into repository DB, then query quickly."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_import = sub.add_parser("import", help="Import Excel into SQLite + CSV")
    p_import.add_argument("--excel", required=True, help="Path of modem apn.xlsx")

    p_query = sub.add_parser("query", help="Query imported NV data by keyword")
    p_query.add_argument("--keyword", required=True, help="Keyword to search")
    p_query.add_argument("--limit", type=int, default=100, help="Maximum returned rows")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "import":
        excel_path = Path(args.excel)
        df = load_excel(excel_path)
        if df.empty:
            print("Excel has no valid rows.")
            return
        save_to_repository(df)
        print(f"Imported {len(df)} rows into {DB_PATH}")
        return

    if args.cmd == "query":
        result = query_nv(args.keyword, limit=args.limit)
        if result.empty:
            print("No matched rows.")
        else:
            print(result.to_string(index=False))


if __name__ == "__main__":
    main()
