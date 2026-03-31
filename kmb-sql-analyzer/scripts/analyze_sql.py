#!/usr/bin/env python3
"""
SQL Analyzer for Metabase Migration

Analyzes SQL queries and generates migration plans including:
- Model SQL (raw granularity)
- MBQL Question configuration
- Visualization settings
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class SQLAnalyzer:
    """Analyzes SQL structure for Metabase migration."""

    def __init__(self, sql: str, database_id: int = 4):
        self.sql = sql.strip()
        self.database_id = database_id
        self.analysis = {}

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return migration plan."""
        self.analysis = {
            "source_tables": self._extract_tables(),
            "table_types": self._determine_table_types(),
            "select_fields": self._extract_select_fields(),
            "group_by": self._extract_group_by(),
            "filters": self._extract_filters(),
            "order_by": self._extract_order_by(),
            "limit": self._extract_limit(),
        }

        return {
            "analysis": self.analysis,
            "model": self._generate_model(),
            "metrics": self._suggest_metrics(),
            "questions": self._generate_questions(),
            "visualization": self._suggest_visualization(),
        }

    def _extract_tables(self) -> List[str]:
        """Extract source tables from SQL."""
        # Match FROM and JOIN clauses
        tables = []

        # FROM clause
        from_match = re.search(r'FROM\s+(\w+)', self.sql, re.IGNORECASE)
        if from_match:
            tables.append(from_match.group(1))

        # JOIN clauses
        join_matches = re.findall(r'JOIN\s+(\w+)', self.sql, re.IGNORECASE)
        tables.extend(join_matches)

        return tables

    def _determine_table_types(self) -> List[str]:
        """Determine if tables are I表 or S表."""
        types = []
        for table in self.analysis.get("source_tables", []):
            if table.endswith("_i_d"):
                types.append("I表(增量)")
            elif table.endswith("_s_d"):
                types.append("S表(快照)")
            else:
                types.append("未知")
        return types

    def _extract_select_fields(self) -> Dict[str, List[Dict]]:
        """Extract SELECT fields, separating dimensions and metrics."""
        fields = {"dimensions": [], "metrics": [], "calculated": []}

        # Extract content between SELECT and FROM
        select_match = re.search(r'SELECT\s+(.+?)\s+FROM', self.sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return fields

        select_clause = select_match.group(1)

        # Split by comma, but be careful with nested parentheses
        field_parts = self._split_fields(select_clause)

        for part in field_parts:
            part = part.strip()
            if not part:
                continue

            # Check for aggregation functions
            agg_match = re.match(r'(COUNT|SUM|AVG|MIN|MAX)\s*\((.+?)\)(?:\s+AS\s+(\w+))?', part, re.IGNORECASE)

            if agg_match:
                func_name = agg_match.group(1).upper()
                inner = agg_match.group(2).strip()
                alias = agg_match.group(3) if agg_match.group(3) else f"{func_name.lower()}_value"

                # Check for DISTINCT
                distinct = "DISTINCT" in inner.upper()
                inner_clean = re.sub(r'DISTINCT\s+', '', inner, flags=re.IGNORECASE).strip()

                fields["metrics"].append({
                    "name": alias,
                    "function": func_name,
                    "distinct": distinct,
                    "field": inner_clean,
                    "original": part
                })
            else:
                # Dimension field
                # Handle alias
                alias_match = re.match(r'(.+?)\s+AS\s+(\w+)', part, re.IGNORECASE)
                if alias_match:
                    fields["dimensions"].append({
                        "name": alias_match.group(2),
                        "expression": alias_match.group(1).strip(),
                        "original": part
                    })
                else:
                    fields["dimensions"].append({
                        "name": part,
                        "expression": part,
                        "original": part
                    })

        return fields

    def _split_fields(self, clause: str) -> List[str]:
        """Split SELECT clause by comma, respecting parentheses."""
        fields = []
        current = ""
        depth = 0

        for char in clause:
            if char == '(':
                depth += 1
                current += char
            elif char == ')':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                fields.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            fields.append(current.strip())

        return fields

    def _extract_group_by(self) -> List[str]:
        """Extract GROUP BY fields."""
        group_match = re.search(r'GROUP\s+BY\s+(.+?)(?:\s+(?:ORDER|LIMIT|HAVING|$))', self.sql, re.IGNORECASE | re.DOTALL)
        if not group_match:
            return []

        group_clause = group_match.group(1)
        # Split by comma
        fields = [f.strip() for f in group_clause.split(',')]
        return fields

    def _extract_filters(self) -> Dict[str, Any]:
        """Extract WHERE conditions."""
        filters = {"time_range": None, "conditions": []}

        where_match = re.search(r'WHERE\s+(.+?)(?:\s+(?:GROUP|ORDER|LIMIT|$))', self.sql, re.IGNORECASE | re.DOTALL)
        if not where_match:
            return filters

        where_clause = where_match.group(1).strip()

        # Look for ds/BETWEEN patterns (time range)
        time_match = re.search(r'ds\s+BETWEEN\s+[\'"]([^\'"]+)[\'"]\s+AND\s+[\'"]([^\'"]+)[\'"]', where_clause, re.IGNORECASE)
        if time_match:
            filters["time_range"] = {
                "field": "ds",
                "start": time_match.group(1),
                "end": time_match.group(2)
            }

        # Extract other conditions (simplified)
        # Remove time range condition
        other_conditions = re.sub(r'ds\s+BETWEEN\s+[\'"][^\'"]+[\'"]\s+AND\s+[\'"][^\'"]+[\'"]', '', where_clause, flags=re.IGNORECASE)
        other_conditions = re.sub(r'^\s*AND\s+|\s+AND\s*$', '', other_conditions, flags=re.IGNORECASE)

        if other_conditions.strip():
            filters["conditions"] = [c.strip() for c in other_conditions.split(' AND ') if c.strip()]

        return filters

    def _extract_order_by(self) -> List[Dict]:
        """Extract ORDER BY clauses."""
        order_match = re.search(r'ORDER\s+BY\s+(.+?)(?:\s+LIMIT|$)', self.sql, re.IGNORECASE | re.DOTALL)
        if not order_match:
            return []

        order_clause = order_match.group(1)
        orders = []

        for part in order_clause.split(','):
            part = part.strip()
            if re.search(r'DESC', part, re.IGNORECASE):
                field = re.sub(r'\s+DESC', '', part, flags=re.IGNORECASE).strip()
                orders.append({"field": field, "direction": "desc"})
            else:
                field = re.sub(r'\s+ASC', '', part, flags=re.IGNORECASE).strip()
                orders.append({"field": field, "direction": "asc"})

        return orders

    def _extract_limit(self) -> Optional[int]:
        """Extract LIMIT value."""
        limit_match = re.search(r'LIMIT\s+(\d+)', self.sql, re.IGNORECASE)
        if limit_match:
            return int(limit_match.group(1))
        return None

    def _generate_model(self) -> Dict[str, Any]:
        """Generate Model SQL and configuration."""
        select_fields = self.analysis.get("select_fields", {})
        tables = self.analysis.get("source_tables", [])
        table_types = self.analysis.get("table_types", [])
        filters = self.analysis.get("filters", {})

        # Build Model SELECT clause (remove aggregations)
        model_fields = []

        # Add dimension fields
        for dim in select_fields.get("dimensions", []):
            expr = dim["expression"]
            name = dim["name"]

            # Check for date conversion
            date_match = re.search(r'STR_TO_DATE\s*\((.+?),', expr, re.IGNORECASE)
            if date_match:
                model_fields.append(f"  {expr}")
            # Check for CASE WHEN
            elif re.search(r'CASE\s+WHEN', expr, re.IGNORECASE):
                model_fields.append(f"  {expr}")
            else:
                model_fields.append(f"  {expr}")

        # Add fields from aggregations (the inner field)
        for metric in select_fields.get("metrics", []):
            field = metric["field"]
            # Skip if it's a complex expression
            if not re.match(r'^[\w\.]+$', field):
                continue
            # Avoid duplicates
            if field not in [d["name"] for d in select_fields.get("dimensions", [])]:
                model_fields.append(f"  {field}")

        # Build WHERE clause based on table type
        where_conditions = []

        for i, table in enumerate(tables):
            if i < len(table_types) and "S表" in table_types[i]:
                # S表: 固定T+1快照
                where_conditions.append(
                    "ds = DATE_FORMAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), '%Y%m%d')"
                )
            # I表: 不限制ds

        # Add other conditions from original SQL (excluding time range)
        for cond in filters.get("conditions", []):
            where_conditions.append(cond)

        # Build Model SQL
        model_sql = f"SELECT\n"
        model_sql += ",\n".join(model_fields)
        model_sql += f"\nFROM {tables[0]}\n" if tables else "\nFROM table_name\n"

        if where_conditions:
            model_sql += "WHERE " + "\n  AND ".join(where_conditions) + "\n"

        # Determine table type handling description
        table_handling = []
        for i, table in enumerate(tables):
            ttype = table_types[i] if i < len(table_types) else "未知"
            if "I表" in ttype:
                table_handling.append(f"{table}: I表，不限制ds")
            elif "S表" in ttype:
                table_handling.append(f"{table}: S表，固定T+1快照")

        return {
            "sql": model_sql.strip(),
            "fields": [f.strip() for f in model_fields],
            "table_type_handling": "; ".join(table_handling) if table_handling else "未识别表类型"
        }

    def _suggest_metrics(self) -> List[Dict]:
        """Suggest Metrics for complex calculations."""
        # For now, return empty - metrics creation is optional
        # Could be enhanced to detect complex CASE WHEN patterns
        return []

    def _generate_questions(self) -> List[Dict]:
        """Generate MBQL Question configurations."""
        select_fields = self.analysis.get("select_fields", {})
        group_by = self.analysis.get("group_by", [])

        questions = []

        # Build breakout from GROUP BY
        breakout = []
        for gb_field in group_by:
            # Map common field names
            if "day" in gb_field.lower() or "date" in gb_field.lower():
                breakout.append(["field", gb_field, {"temporal-unit": "day"}])
            else:
                breakout.append(["field", gb_field])

        # Build aggregations
        aggregations = []
        for metric in select_fields.get("metrics", []):
            func = metric["function"].lower()
            field = metric["field"]
            name = metric["name"]

            # Build MBQL aggregation
            if func == "count" and metric.get("distinct"):
                inner = ["distinct", ["field", field]]
            elif func == "count":
                inner = ["count"]
            elif func == "sum":
                # Check for CASE WHEN in SUM
                case_match = re.search(r'CASE\s+WHEN\s+(.+?)\s+THEN\s+(.+?)\s+END', field, re.IGNORECASE)
                if case_match:
                    condition = case_match.group(1).strip()
                    then_value = case_match.group(2).strip()
                    # Simplified case parsing
                    inner = ["sum", ["case", [[self._parse_condition(condition), ["field", then_value]]]]]
                else:
                    inner = ["sum", ["field", field]]
            elif func == "avg":
                inner = ["avg", ["field", field]]
            else:
                inner = [func, ["field", field]]

            # Wrap with aggregation-options for naming
            agg = ["aggregation-options", inner, {"name": name, "display-name": name}]
            aggregations.append(agg)

        question = {
            "name": "迁移图表",
            "breakout": breakout,
            "aggregation": aggregations,
            "filter": [],
            "source_table": "card__{model_id}"
        }

        questions.append(question)
        return questions

    def _parse_condition(self, condition: str) -> List:
        """Parse SQL condition to MBQL filter format."""
        # Simplified parsing - handles basic =, !=, <, >
        eq_match = re.match(r'(\w+)\s*=\s*[\'"]?([^\'"]+)[\'"]?', condition)
        if eq_match:
            return ["=", ["field", eq_match.group(1)], eq_match.group(2)]

        neq_match = re.match(r'(\w+)\s*!=\s*[\'"]?([^\'"]+)[\'"]?', condition)
        if neq_match:
            return ["!=", ["field", neq_match.group(1)], neq_match.group(2)]

        # Default to raw condition
        return condition

    def _suggest_visualization(self) -> Dict[str, Any]:
        """Suggest visualization configuration."""
        select_fields = self.analysis.get("select_fields", {})
        group_by = self.analysis.get("group_by", [])

        # Default to line chart
        viz = {
            "display": "line",
            "graph.dimensions": [gb for gb in group_by],
            "graph.metrics": [m["name"] for m in select_fields.get("metrics", [])],
            "series_settings": {},
            "column_settings": {}
        }

        # Check for rate/percentage metrics
        for metric in select_fields.get("metrics", []):
            name = metric["name"].lower()
            if "rate" in name or "percent" in name or "ratio" in name or "转化" in name:
                viz["column_settings"][f'["name","{metric["name"]}"]'] = {
                    "number_style": "percent"
                }
                viz["series_settings"][metric["name"]] = {"axis": "right", "display": "line"}

        return viz


def main():
    parser = argparse.ArgumentParser(description="Analyze SQL for Metabase migration")
    parser.add_argument("--sql-file", help="Path to SQL file")
    parser.add_argument("--sql", help="SQL string directly")
    parser.add_argument("--database", type=int, default=4, help="Database ID")
    parser.add_argument("--output", "-o", default="migration_plan.json", help="Output file")
    parser.add_argument("--output-model-only", action="store_true", help="Output only Model SQL to stdout")

    args = parser.parse_args()

    # Get SQL input
    if args.sql_file:
        with open(args.sql_file, 'r') as f:
            sql = f.read()
    elif args.sql:
        sql = args.sql
    else:
        print("Error: Provide --sql-file or --sql", file=sys.stderr)
        sys.exit(1)

    # Analyze
    analyzer = SQLAnalyzer(sql, args.database)
    result = analyzer.analyze()

    if args.output_model_only:
        print(result["model"]["sql"])
    else:
        # Write to file
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Migration plan written to: {args.output}")
        print(f"\nAnalysis Summary:")
        print(f"  Tables: {', '.join(result['analysis']['source_tables'])}")
        print(f"  Table Types: {', '.join(result['analysis']['table_types'])}")
        print(f"  Dimensions: {len(result['analysis']['select_fields']['dimensions'])}")
        print(f"  Metrics: {len(result['analysis']['select_fields']['metrics'])}")
        print(f"  GROUP BY: {', '.join(result['analysis']['group_by'])}")


if __name__ == "__main__":
    main()
