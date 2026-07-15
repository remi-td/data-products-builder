#!/usr/bin/env python3
"""
Teradata Source Image SQL Compiler.
Generates optimized, syntactically correct Teradata SQL scripts to run historization
(SCD Type 2) processes using Jinja2 templates.
"""

import os
import sys
import json
import argparse

def install_and_import_jinja2():
    try:
        import jinja2
        return jinja2
    except ImportError:
        print("Error: jinja2 is required to run this script.", file=sys.stderr)
        print("Please install it using your Python package manager:", file=sys.stderr)
        print("  pip install jinja2", file=sys.stderr)
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Compile Teradata Source Image SQL template into runnable SQL."
    )
    parser.add_argument(
        "-c", "--config", 
        help="Path to JSON configuration file containing metadata."
    )
    parser.add_argument(
        "--source-table", 
        help="Name of the source staging table."
    )
    parser.add_argument(
        "--target-table", 
        help="Name of the target table."
    )
    parser.add_argument(
        "--key-columns", 
        help="Comma-separated primary key columns."
    )
    parser.add_argument(
        "--time-change-column", 
        help="Column representing record change timestamp (e.g. Valid_from)."
    )
    parser.add_argument(
        "--tracked-columns", 
        help="Comma-separated value columns to track."
    )
    parser.add_argument(
        "--columns-with-types", 
        help="Comma-separated column definition with types (e.g., 'PK:INT,Value_txt:VARCHAR(1000)')."
    )
    parser.add_argument(
        "--use-valid-to", 
        action="store_true",
        help="Enable closed-ended validity periods using valid_to."
    )
    parser.add_argument(
        "--valid-to-column", 
        help="Column representing record end timestamp (if --use-valid-to is set)."
    )
    parser.add_argument(
        "--valid-period-column", 
        default="Valid_per",
        help="Name of target period column (default: Valid_per)."
    )
    parser.add_argument(
        "-o", "--output", 
        help="Path to output compiled SQL file. If omitted, prints to stdout."
    )
    parser.add_argument(
        "-t", "--template", 
        help="Path to Jinja2 template file. If omitted, uses default history_load.sql.jt next to this script."
    )
    return parser.parse_args()

def load_config_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: Config file not found at {filepath}", file=sys.stderr)
        sys.exit(1)
    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON configuration file: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    args = parse_args()
    config = {}

    # Load configuration file if provided
    if args.config:
        config = load_config_file(args.config)

    # CLI arguments override config file values
    source_table = args.source_table or config.get("source_table")
    target_table = args.target_table or config.get("target_table")
    
    key_cols_str = args.key_columns or config.get("key_columns")
    if isinstance(key_cols_str, str):
        key_columns = [k.strip() for k in key_cols_str.split(",") if k.strip()]
    else:
        key_columns = key_cols_str or []

    time_change_column = args.time_change_column or config.get("time_change_column")
    
    tracked_cols_str = args.tracked_columns or config.get("tracked_columns")
    if isinstance(tracked_cols_str, str):
        tracked_columns = [t.strip() for t in tracked_cols_str.split(",") if t.strip()]
    else:
        tracked_columns = tracked_cols_str or []

    use_valid_to = args.use_valid_to or config.get("use_valid_to", False)
    valid_to_column = args.valid_to_column or config.get("valid_to_column")
    valid_period_column = args.valid_period_column or config.get("valid_period_column", "Valid_per")

    # Handle columns with types
    cols_with_types = []
    cols_with_types_str = args.columns_with_types or config.get("columns_with_types")
    
    if isinstance(cols_with_types_str, str):
        for item in cols_with_types_str.split(","):
            if ":" in item:
                col_name, col_type = item.split(":", 1)
                cols_with_types.append({
                    "name": col_name.strip(),
                    "type": col_type.strip()
                })
    elif isinstance(cols_with_types_str, list):
        cols_with_types = cols_with_types_str
    elif isinstance(cols_with_types_str, dict):
        for name, typ in cols_with_types_str.items():
            cols_with_types.append({
                "name": name.strip(),
                "type": typ.strip()
            })

    # Basic validations
    errors = []
    if not source_table:
        errors.append("source_table is required")
    if not target_table:
        errors.append("target_table is required")
    if not key_columns:
        errors.append("key_columns is required")
    if not time_change_column:
        errors.append("time_change_column is required")
    if not tracked_columns:
        errors.append("tracked_columns is required")
    if not cols_with_types:
        errors.append("columns_with_types definition is required (maps columns to Teradata types)")
    if use_valid_to and not valid_to_column:
        errors.append("valid_to_column is required when use_valid_to is enabled")

    if errors:
        print("Validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    # Determine template path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = args.template or os.path.join(script_dir, "../templates/history_load.sql.jt")
    
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    with open(template_path, 'r') as f:
        template_content = f.read()

    # Import jinja2
    jinja2 = install_and_import_jinja2()
    
    # Render template
    try:
        env = jinja2.Environment()
        template = env.from_string(template_content)
        rendered_sql = template.render(
            source_table=source_table,
            target_table=target_table,
            key_columns=key_columns,
            time_change_column=time_change_column,
            tracked_columns=tracked_columns,
            use_valid_to=use_valid_to,
            valid_to_column=valid_to_column,
            valid_period_column=valid_period_column,
            columns_with_types=cols_with_types
        )
    except Exception as e:
        print(f"Error compiling template: {e}", file=sys.stderr)
        sys.exit(1)

    # Output logic
    if args.output:
        with open(args.output, 'w') as f:
            f.write(rendered_sql)
        print(f"Successfully compiled Teradata SQL to: {args.output}")
    else:
        print(rendered_sql)

if __name__ == "__main__":
    main()
