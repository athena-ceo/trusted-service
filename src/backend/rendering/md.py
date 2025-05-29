from typing import Iterable, Callable, Any

from src.backend.text_analysis.base_models import FIELD_NAME_SCORINGS


def build_markdown_table(
        rows: Iterable[any],
        column_names: list[str],
        producers: list[Callable[[any], str]],
) -> str:
    column_names = [f":blue-background[{column_name}]" for column_name in column_names]
    md = "| " + " | ".join(column_names) + " |\n"
    md += "| - " * len(column_names) + "|\n"

    for row in rows:
        values: list[str] = [
            val if (val := producer(row).replace("\n", " ")) else ""
            for producer in producers
        ]
        md += "| " + " | ".join(values) + " |\n"

    return md

def build_markdown_table_intentions(analysis_result: dict[str, Any]) -> str:
    rows = analysis_result[FIELD_NAME_SCORINGS]
    column_names = ["Intention", "Score", "Justification"]
    producers: list[Callable[[any], str]] = [
        lambda obj: obj["intention_label"],
        lambda obj: str(obj["score"]),
        lambda obj: obj["justification"],
    ]
    return build_markdown_table(rows, column_names, producers, )


