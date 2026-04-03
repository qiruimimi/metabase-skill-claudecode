#!/usr/bin/env python3
"""
SQL Analyzer for Metabase Migration

Analyzes SQL queries and generates migration plans including:
- Model SQL (raw granularity)
- Delivery decisions for MBQL vs native questions
- MBQL Question configuration when feasible
- Visualization settings
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLAnalyzer:
    """Analyzes SQL structure for Metabase migration."""

    def __init__(self, sql: str, database_id: int = 4):
        self.sql = sql.strip()
        self.database_id = database_id
        self.analysis: Dict[str, Any] = {}

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return migration plan."""
        source_tables = self._extract_tables()
        self.analysis = {"source_tables": source_tables}
        self.analysis["table_types"] = self._determine_table_types()
        self.analysis["select_fields"] = self._extract_select_fields()
        self.analysis["group_by"] = self._extract_group_by()
        self.analysis["filters"] = self._extract_filters()
        self.analysis["order_by"] = self._extract_order_by()
        self.analysis["limit"] = self._extract_limit()
        self.analysis["complexity_flags"] = self._detect_complexity_flags()

        delivery_decisions = self._recommend_delivery_decisions()
        return {
            "analysis": self.analysis,
            "delivery_decisions": delivery_decisions,
            "model": self._generate_model(),
            "metrics": self._suggest_metrics(),
            "questions": self._generate_questions(delivery_decisions),
            "visualization": self._suggest_visualization(),
        }

    def _extract_tables(self) -> List[str]:
        """Extract source tables from SQL."""
        matches = re.findall(r"\b(?:FROM|JOIN)\s+([a-zA-Z0-9_.]+)", self.sql, re.IGNORECASE)
        tables: List[str] = []
        seen: set[str] = set()
        for table in matches:
            if table not in seen:
                tables.append(table)
                seen.add(table)
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

    def _extract_select_fields(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract SELECT fields, separating dimensions and metrics."""
        fields: Dict[str, List[Dict[str, Any]]] = {"dimensions": [], "metrics": [], "calculated": []}

        select_match = re.search(r"SELECT\s+(.+?)\s+FROM", self.sql, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return fields

        select_clause = select_match.group(1)
        field_parts = self._split_fields(select_clause)

        for part in field_parts:
            part = part.strip()
            if not part:
                continue

            agg_match = re.match(
                r"(COUNT|SUM|AVG|MIN|MAX)\s*\((.+?)\)(?:\s+AS\s+([`\"\w\u4e00-\u9fff]+))?",
                part,
                re.IGNORECASE,
            )

            if agg_match:
                func_name = agg_match.group(1).upper()
                inner = agg_match.group(2).strip()
                alias = agg_match.group(3) if agg_match.group(3) else f"{func_name.lower()}_value"
                alias = alias.strip("`\"")
                distinct = "DISTINCT" in inner.upper()
                inner_clean = re.sub(r"DISTINCT\s+", "", inner, flags=re.IGNORECASE).strip()

                fields["metrics"].append(
                    {
                        "name": alias,
                        "function": func_name,
                        "distinct": distinct,
                        "field": inner_clean,
                        "original": part,
                    }
                )
                continue

            alias_match = re.match(r"(.+?)\s+AS\s+([`\"\w\u4e00-\u9fff]+)", part, re.IGNORECASE)
            if alias_match:
                fields["dimensions"].append(
                    {
                        "name": alias_match.group(2).strip("`\""),
                        "expression": alias_match.group(1).strip(),
                        "original": part,
                    }
                )
            else:
                fields["dimensions"].append(
                    {
                        "name": part.strip("`\""),
                        "expression": part,
                        "original": part,
                    }
                )

        return fields

    def _split_fields(self, clause: str) -> List[str]:
        """Split SELECT clause by comma, respecting parentheses."""
        fields = []
        current = ""
        depth = 0

        for char in clause:
            if char == "(":
                depth += 1
                current += char
            elif char == ")":
                depth -= 1
                current += char
            elif char == "," and depth == 0:
                fields.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            fields.append(current.strip())

        return fields

    def _extract_group_by(self) -> List[str]:
        """Extract GROUP BY fields."""
        group_match = re.search(
            r"GROUP\s+BY\s+(.+?)(?=\s+(?:ORDER|LIMIT|HAVING)\b|$)",
            self.sql,
            re.IGNORECASE | re.DOTALL,
        )
        if not group_match:
            return []

        group_clause = group_match.group(1)
        return [field.strip() for field in group_clause.split(",")]

    def _extract_filters(self) -> Dict[str, Any]:
        """Extract WHERE conditions."""
        filters: Dict[str, Any] = {"time_range": None, "conditions": []}

        where_match = re.search(
            r"WHERE\s+(.+?)(?=\s+(?:GROUP|ORDER|LIMIT)\b|$)",
            self.sql,
            re.IGNORECASE | re.DOTALL,
        )
        if not where_match:
            return filters

        where_clause = where_match.group(1).strip()

        time_match = re.search(
            r"ds\s+BETWEEN\s+[\'\"]([^\'\"]+)[\'\"]\s+AND\s+[\'\"]([^\'\"]+)[\'\"]",
            where_clause,
            re.IGNORECASE,
        )
        if time_match:
            filters["time_range"] = {
                "field": "ds",
                "start": time_match.group(1),
                "end": time_match.group(2),
            }

        other_conditions = re.sub(
            r"ds\s+BETWEEN\s+[\'\"][^\'\"]+[\'\"]\s+AND\s+[\'\"][^\'\"]+[\'\"]",
            "",
            where_clause,
            flags=re.IGNORECASE,
        )
        other_conditions = re.sub(r"^\s*AND\s+|\s+AND\s*$", "", other_conditions, flags=re.IGNORECASE)

        if other_conditions.strip():
            filters["conditions"] = [cond.strip() for cond in other_conditions.split(" AND ") if cond.strip()]

        return filters

    def _detect_complexity_flags(self) -> Dict[str, Any]:
        """Detect SQL features that affect migration strategy."""
        return {
            "has_template_tags": bool(re.search(r"{{\s*[\w.-]+\s*}}", self.sql)),
            "has_cte": bool(re.search(r"^\s*WITH\b", self.sql, re.IGNORECASE)),
            "has_window_functions": bool(re.search(r"\bOVER\s*\(", self.sql, re.IGNORECASE)),
            "has_union": bool(re.search(r"\bUNION\b", self.sql, re.IGNORECASE)),
            "has_nested_subquery": bool(re.search(r"\bFROM\s*\(", self.sql, re.IGNORECASE)),
            "has_case_when": bool(re.search(r"\bCASE\b", self.sql, re.IGNORECASE)),
            "has_multiple_tables": len(self.analysis.get("source_tables", [])) > 1,
        }

    def _extract_order_by(self) -> List[Dict[str, str]]:
        """Extract ORDER BY clauses."""
        order_match = re.search(r"ORDER\s+BY\s+(.+?)(?:\s+LIMIT|$)", self.sql, re.IGNORECASE | re.DOTALL)
        if not order_match:
            return []

        order_clause = order_match.group(1)
        orders = []

        for part in order_clause.split(","):
            part = part.strip()
            if re.search(r"DESC", part, re.IGNORECASE):
                field = re.sub(r"\s+DESC", "", part, flags=re.IGNORECASE).strip()
                orders.append({"field": field, "direction": "desc"})
            else:
                field = re.sub(r"\s+ASC", "", part, flags=re.IGNORECASE).strip()
                orders.append({"field": field, "direction": "asc"})

        return orders

    def _extract_limit(self) -> Optional[int]:
        """Extract LIMIT value."""
        limit_match = re.search(r"LIMIT\s+(\d+)", self.sql, re.IGNORECASE)
        if limit_match:
            return int(limit_match.group(1))
        return None

    def _generate_model(self) -> Dict[str, Any]:
        """Generate Model SQL and configuration."""
        select_fields = self.analysis.get("select_fields", {})
        tables = self.analysis.get("source_tables", [])
        table_types = self.analysis.get("table_types", [])
        filters = self.analysis.get("filters", {})

        model_fields: List[str] = []
        seen_fields: set[str] = set()

        def append_unique(expr: str):
            normalized = re.sub(r"\s+", " ", expr).strip().lower()
            if normalized not in seen_fields:
                model_fields.append(expr)
                seen_fields.add(normalized)

        for dim in select_fields.get("dimensions", []):
            append_unique(f"  {dim['expression']}")

        for metric in select_fields.get("metrics", []):
            field = metric["field"]
            if not re.match(r"^[\w\.]+$", field):
                continue
            if field not in [dim["name"] for dim in select_fields.get("dimensions", [])]:
                append_unique(f"  {field}")

        if any("S表" in table_type for table_type in table_types):
            append_unique("  ds")
            append_unique("  STR_TO_DATE(ds, '%Y%m%d') AS ds_time")

        where_conditions = []
        for index, table in enumerate(tables):
            if index < len(table_types) and "S表" in table_types[index]:
                where_conditions.append(
                    "ds = DATE_FORMAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), '%Y%m%d')"
                )

        for cond in filters.get("conditions", []):
            where_conditions.append(cond)

        model_sql = "SELECT\n"
        model_sql += ",\n".join(model_fields)
        model_sql += f"\nFROM {tables[0]}\n" if tables else "\nFROM table_name\n"

        if where_conditions:
            model_sql += "WHERE " + "\n  AND ".join(where_conditions) + "\n"

        table_handling = []
        for index, table in enumerate(tables):
            ttype = table_types[index] if index < len(table_types) else "未知"
            if "I表" in ttype:
                table_handling.append(f"{table}: I表，不限制ds")
            elif "S表" in ttype:
                table_handling.append(f"{table}: S表，固定T+1快照")

        complexity_flags = self.analysis.get("complexity_flags", {})
        requires_manual_review = bool(
            complexity_flags.get("has_template_tags")
            or complexity_flags.get("has_cte")
            or complexity_flags.get("has_window_functions")
            or complexity_flags.get("has_union")
        )

        return {
            "sql": model_sql.strip(),
            "fields": [field.strip() for field in model_fields],
            "table_type_handling": "; ".join(table_handling) if table_handling else "未识别表类型",
            "manual_review_required": requires_manual_review,
            "notes": (
                "原 SQL 复杂度较高，自动生成的 Model SQL 仅供起草，创建前需要人工复核。"
                if requires_manual_review
                else "自动生成的 Model SQL 可作为后续建模起点。"
            ),
        }

    def _recommend_delivery_decisions(self) -> Dict[str, Any]:
        """Recommend downstream delivery pattern for Model and Question layers."""
        flags = self.analysis.get("complexity_flags", {})
        source_tables = self.analysis.get("source_tables", [])
        group_by = self.analysis.get("group_by", [])
        select_fields = self.analysis.get("select_fields", {})
        metric_count = len(select_fields.get("metrics", []))

        native_reasons = []
        if flags.get("has_template_tags"):
            native_reasons.append("包含 template-tag/dashboard 变量")
        if flags.get("has_cte"):
            native_reasons.append("包含 CTE")
        if flags.get("has_window_functions"):
            native_reasons.append("包含窗口函数")
        if flags.get("has_union"):
            native_reasons.append("包含 UNION")

        question_mode = "native" if native_reasons else "mbql"
        question_mode_reason = (
            "；".join(native_reasons)
            if native_reasons
            else "可表达为基于 card__id 的 breakout / aggregation / filter / joins / expressions"
        )

        shared_model_candidate = {
            "recommended": bool(metric_count or len(source_tables) > 1 or group_by),
            "reason": (
                "查询包含聚合、分组或多表字段，适合先沉淀为可复用 Model"
                if (metric_count or len(source_tables) > 1 or group_by)
                else "查询已接近明细形态，可直接评估是否复用已有 Model/Card"
            ),
        }

        shared_question_base_candidate = {
            "recommended": question_mode == "mbql" and bool(group_by or metric_count),
            "reason": (
                "MBQL 问题可复用共享 card__ 基座，再拆分成多个独立 card"
                if question_mode == "mbql" and bool(group_by or metric_count)
                else "当前查询更适合作为独立 native question 或一次性问题"
            ),
        }

        if question_mode == "native" and flags.get("has_template_tags"):
            dashboard_parameter_strategy = "variable"
            dashboard_parameter_strategy_reason = (
                "当前问题直接依赖 template-tag，优先用 dashboard variable 映射；"
                "若同页还包含 MBQL 卡片，在页面级计划里升级为 mixed"
            )
        elif question_mode == "mbql":
            dashboard_parameter_strategy = "dimension"
            dashboard_parameter_strategy_reason = "当前问题优先通过字段维度做 dashboard parameter mapping"
        else:
            dashboard_parameter_strategy = "mixed"
            dashboard_parameter_strategy_reason = "查询复杂度较高，通常需要结合 variable 与 dimension 做页面级参数策略"

        return {
            "question_mode": question_mode,
            "question_mode_reason": question_mode_reason,
            "shared_model_candidate": shared_model_candidate,
            "shared_question_base_candidate": shared_question_base_candidate,
            "dashboard_parameter_strategy": dashboard_parameter_strategy,
            "dashboard_parameter_strategy_reason": dashboard_parameter_strategy_reason,
        }

    def _suggest_metrics(self) -> List[Dict[str, Any]]:
        """Suggest Metrics for complex calculations."""
        return []

    def _generate_questions(self, delivery_decisions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Question configurations."""
        select_fields = self.analysis.get("select_fields", {})
        group_by = self.analysis.get("group_by", [])

        breakout = []
        for gb_field in group_by:
            if "day" in gb_field.lower() or "date" in gb_field.lower():
                breakout.append(["field", gb_field, {"temporal-unit": "day"}])
            else:
                breakout.append(["field", gb_field])

        aggregations = []
        for metric in select_fields.get("metrics", []):
            func = metric["function"].lower()
            field = metric["field"]
            name = metric["name"]

            if func == "count" and metric.get("distinct"):
                inner = ["distinct", ["field", field]]
            elif func == "count":
                inner = ["count"]
            elif func == "sum":
                case_match = re.search(r"CASE\s+WHEN\s+(.+?)\s+THEN\s+(.+?)\s+END", field, re.IGNORECASE)
                if case_match:
                    condition = case_match.group(1).strip()
                    then_value = case_match.group(2).strip()
                    inner = ["sum", ["case", [[self._parse_condition(condition), ["field", then_value]]]]]
                else:
                    inner = ["sum", ["field", field]]
            elif func == "avg":
                inner = ["avg", ["field", field]]
            else:
                inner = [func, ["field", field]]

            aggregations.append(["aggregation-options", inner, {"name": name, "display-name": name}])

        if delivery_decisions["question_mode"] == "native":
            return [
                {
                    "name": "迁移图表",
                    "question_mode": "native",
                    "native_sql": self.sql,
                    "dashboard_parameter_strategy": delivery_decisions["dashboard_parameter_strategy"],
                    "notes": delivery_decisions["question_mode_reason"],
                }
            ]

        return [
            {
                "name": "迁移图表",
                "question_mode": "mbql",
                "shared_question_base_candidate": delivery_decisions["shared_question_base_candidate"]["recommended"],
                "dashboard_parameter_strategy": delivery_decisions["dashboard_parameter_strategy"],
                "query": {
                    "breakout": breakout,
                    "aggregation": aggregations,
                    "filter": [],
                    "source-table": "card__{model_id}",
                },
            }
        ]

    def _parse_condition(self, condition: str) -> List[Any] | str:
        """Parse SQL condition to MBQL filter format."""
        eq_match = re.match(r"(\w+)\s*=\s*[\'\"]?([^\'\"]+)[\'\"]?", condition)
        if eq_match:
            return ["=", ["field", eq_match.group(1)], eq_match.group(2)]

        neq_match = re.match(r"(\w+)\s*!=\s*[\'\"]?([^\'\"]+)[\'\"]?", condition)
        if neq_match:
            return ["!=", ["field", neq_match.group(1)], neq_match.group(2)]

        return condition

    def _suggest_visualization(self) -> Dict[str, Any]:
        """Suggest visualization configuration."""
        select_fields = self.analysis.get("select_fields", {})
        group_by = self.analysis.get("group_by", [])

        viz = {
            "display": "line",
            "graph.dimensions": [gb for gb in group_by],
            "graph.metrics": [metric["name"] for metric in select_fields.get("metrics", [])],
            "series_settings": {},
            "column_settings": {},
        }

        for metric in select_fields.get("metrics", []):
            name = metric["name"].lower()
            if "rate" in name or "percent" in name or "ratio" in name or "转化" in name:
                viz["column_settings"][f'["name","{metric["name"]}"]'] = {"number_style": "percent"}
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

    if args.sql_file:
        with open(args.sql_file, "r") as f:
            sql = f.read()
    elif args.sql:
        sql = args.sql
    else:
        print("Error: Provide --sql-file or --sql", file=sys.stderr)
        sys.exit(1)

    analyzer = SQLAnalyzer(sql, args.database)
    result = analyzer.analyze()

    if args.output_model_only:
        print(result["model"]["sql"])
    else:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Migration plan written to: {args.output}")
        print("\nAnalysis Summary:")
        print(f"  Tables: {', '.join(result['analysis']['source_tables'])}")
        print(f"  Table Types: {', '.join(result['analysis']['table_types'])}")
        print(f"  Dimensions: {len(result['analysis']['select_fields']['dimensions'])}")
        print(f"  Metrics: {len(result['analysis']['select_fields']['metrics'])}")
        print(f"  GROUP BY: {', '.join(result['analysis']['group_by'])}")
        print(f"  Question Mode: {result['delivery_decisions']['question_mode']}")
        print(f"  Dashboard Params: {result['delivery_decisions']['dashboard_parameter_strategy']}")


if __name__ == "__main__":
    main()
