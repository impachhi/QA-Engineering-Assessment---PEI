# PEI Sales ETL QA Framework

## Overview

This project contains a lightweight QA framework for validating sales reporting requirements using source files placed under `SourceData`.

The framework:

- reads all supported source files from the project `SourceData` directory
- loads the working datasets into an in-memory SQLite database
- executes SQL-based test cases from an Excel workbook
- supports one-off SQL execution for ad hoc validation
- generates QA deliverables such as test results and requirement gap documents

## Project Structure

```text
PEI/
+-- SourceData/                     Raw source files used for validation
+-- qa_output/                      Generated QA outputs and report artifacts
+-- framework_utils.py              Shared framework helpers
+-- run_test_case_queries.py        Workbook-driven test execution runner
+-- run_user_query.py               One-off SQL execution runner
+-- source_data_reader.py           Generic source file reader
+-- README.md                       Project usage and structure guide
```

## Source Files

Place source files under `SourceData`.

Current supported file types:

- `.csv`
- `.json`
- `.xls`
- `.xlsx`

Current PEI input files:

- `Customer.xls` - customer master data
- `Order.csv` - order transaction data
- `Shipping.json` - shipping status data

## Core Scripts

### `source_data_reader.py`

Generic directory reader that:

- scans `SourceData`
- reads all supported files
- creates pandas DataFrames keyed by file name
- provides a backward-compatible `read_sales_sources()` wrapper for the PEI dataset

Run:

```powershell
python source_data_reader.py
```

### `framework_utils.py`

Shared framework module that centralizes:

- SQLite in-memory load
- source column normalization
- SQL statement splitting
- SQL execution and formatting
- test case workbook resolution

### `run_test_case_queries.py`

Executes SQL from the Excel test case workbook and writes a markdown result file.

Default run:

```powershell
python run_test_case_queries.py
```

Explicit workbook run:

```powershell
python run_test_case_queries.py --workbook "C:\Users\prasanna.mahale\PycharmProjects\PEI\qa_output\Test_Cases_ETL_Sales_and_Validation.xlsx"
```

### `run_user_query.py`

Runs user-provided SQL directly against the in-memory tables:

- `customers`
- `orders`
- `shipping`

Default run:

```powershell
python run_user_query.py
```

Inline query run:

```powershell
python run_user_query.py --query "SELECT * FROM customers LIMIT 5;"
```

SQL file run:

```powershell
python run_user_query.py --file "C:\path\to\query.sql"
```

## Available SQLite Tables

The framework maps source data to these SQLite tables:

- `customers(customer_id, first_name, last_name, age, country)`
- `orders(order_id, item, amount, customer_id)`
- `shipping(shipping_id, status, customer_id)`

## Output Artifacts

Generated files are stored under `qa_output`.

Current key outputs:

- `Test_Cases_ETL_Sales_and_Validation.xlsx` - main ETL test case workbook
- `Sales_ETL_Test_Case_Query_Results.md` - SQL execution results from workbook-driven tests
- `explicit_workbook_test_results.md` - explicit workbook execution sample output
- `Sales_Reporting_Requirement_Gap_Document.xlsx` - requirement gap tracker
- `sales_qa_report.md` - consolidated QA summary report

## QA Notes

Current project findings identified during validation:

- shipping cannot be linked reliably to orders at order level because `Order_ID` is missing in shipping
- quantity is not available in the order source, so quantity-based validations are blocked
- some business terms such as `purchased` are ambiguous unless the metric is defined explicitly

## Recommended Usage Flow

1. Place or update source files in `SourceData`
2. Run `source_data_reader.py` to confirm files load correctly
3. Run `run_test_case_queries.py` to execute workbook-based validations
4. Use `run_user_query.py` for ad hoc analysis or requirement-specific checks
5. Review generated artifacts in `qa_output`
