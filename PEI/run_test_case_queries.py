from __future__ import annotations

import argparse
import json
from pathlib import Path

from framework_utils import (
    QA_OUTPUT_DIR,
    build_sqlite_connection,
    execute_statement,
    read_workbook_rows,
    resolve_test_case_workbook,
    split_sql_statements,
)


DEFAULT_OUTPUT_PATH = QA_OUTPUT_DIR / "Sales_ETL_Test_Case_Query_Results.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute workbook-driven SQL test cases against the PEI source data."
    )
    parser.add_argument(
        "--workbook",
        type=Path,
        help="Optional path to the test case workbook. If omitted, the active workbook is auto-detected.",
    )
    parser.add_argument(
        "--sheet",
        default="Test Cases",
        help="Worksheet name containing the test cases. Default: Test Cases",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Markdown output path. Default: {DEFAULT_OUTPUT_PATH}",
    )
    return parser.parse_args()


def generate_results(workbook_path: Path, sheet_name: str, output_path: Path) -> Path:
    test_cases = read_workbook_rows(workbook_path, sheet_name=sheet_name)
    conn = build_sqlite_connection()

    sections = [
        "# Sales ETL Test Case Query Results",
        "",
        f"Workbook: `{workbook_path}`",
        f"Worksheet: `{sheet_name}`",
        "",
        "The source files were loaded into an in-memory SQLite database with tables:",
        "- `customers`",
        "- `orders`",
        "- `shipping`",
        "",
    ]

    for test_case in test_cases:
        sl_no = test_case.get("Sl No")
        test_name = test_case.get("test name")
        sql_text = str(test_case.get("SQL's") or "").strip()

        sections.append(f"## {sl_no}. {test_name}")
        sections.append("")
        sections.append(f"**Description:** {test_case.get('Test Case Description')}")
        sections.append("")
        sections.append(f"**Expectation:** {test_case.get('Test Expectation')}")
        sections.append("")

        if not sql_text or sql_text.upper().startswith("N/A"):
            sections.append(f"**SQL:** `{sql_text}`")
            sections.append("")
            sections.append("**Result:** Not applicable.")
            sections.append("")
            continue

        statements = split_sql_statements(sql_text)
        for index, statement in enumerate(statements, start=1):
            _, markdown_result, _, _ = execute_statement(conn, statement)
            sections.append(f"**Statement {index}:**")
            sections.append("")
            sections.append("```sql")
            sections.append(statement + ";")
            sections.append("```")
            sections.append("")
            sections.append(markdown_result)
            sections.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(sections), encoding="utf-8")
    return output_path


def main() -> None:
    args = parse_args()
    workbook_path = resolve_test_case_workbook(args.workbook)
    output_path = generate_results(workbook_path, args.sheet, args.output)
    print(
        json.dumps(
            {
                "workbook": str(workbook_path),
                "worksheet": args.sheet,
                "result_file": str(output_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
