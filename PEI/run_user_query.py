from __future__ import annotations

import argparse
from pathlib import Path

from framework_utils import (
    QA_OUTPUT_DIR,
    build_sqlite_connection,
    execute_statement,
    split_sql_statements,
)


DEFAULT_QUERY = """
SELECT COUNT(*) AS row_count FROM customers
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one or more user-provided SQL statements against the PEI source tables."
    )
    parser.add_argument(
        "--query",
        help="Inline SQL to execute. If omitted, the script uses the DEFAULT_QUERY variable.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Optional .sql file path. Takes precedence over --query and DEFAULT_QUERY.",
    )
    return parser.parse_args()


def resolve_query_text(args: argparse.Namespace) -> str:
    if args.file:
        return args.file.read_text(encoding="utf-8").strip()
    if args.query:
        return args.query.strip()
    return DEFAULT_QUERY.strip()


def main() -> None:
    args = parse_args()
    query_text = resolve_query_text(args)

    if not query_text:
        raise ValueError("Provide SQL by DEFAULT_QUERY, --query, or --file.")

    statements = split_sql_statements(query_text)
    if not statements:
        raise ValueError("No valid SQL statement found to execute.")

    conn = build_sqlite_connection()

    print("Available tables:")
    print("- customers(customer_id, first_name, last_name, age, country)")
    print("- orders(order_id, item, amount, customer_id)")
    print("- shipping(shipping_id, status, customer_id)")
    print(f"- qa_output directory: {QA_OUTPUT_DIR}")

    for index, statement in enumerate(statements, start=1):
        console_result, _, _, _ = execute_statement(conn, statement)
        print(f"\nStatement {index}\n")
        print(statement + ";")
        print("\nResult\n")
        print(console_result)


if __name__ == "__main__":
    main()
