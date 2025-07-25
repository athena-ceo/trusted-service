from typing import Any, Optional, List

from pydantic import BaseModel

from src.backend.distribution.distribution_email.email2 import Email
from src.backend.text_analysis.base_models import Feature, PREFIX_FRAGMENTS


class ColoredSegment(BaseModel):
    start: int
    end: int
    color: str


class FeatureValue(BaseModel):
    id: str
    label: str
    value: Any
    fragments: Optional[List[tuple[int, int]]] = None
    color: Optional[str]


def build_html_highlighted_text_and_features(text: str,
                                             features: list[Feature],
                                             analysis_result: dict[str, Any]) -> str:
    colors = ["lightblue", "pink", "lightgreen", "cyan", "yellow"]
    index_color = 0
    colored_segments: list[ColoredSegment] = []
    feature_values: list[FeatureValue] = []

    for feature in features:
        # id = feature.id
        label = feature.label
        value = analysis_result[feature.id]
        color: Optional[str] = None
        if not feature.highlight_fragments:
            continue
        fragments = analysis_result[f"{PREFIX_FRAGMENTS}{feature.id}"]
        if not fragments:
            continue
        for fragment in fragments["list"]:
            start = text.find(fragment)
            # print("start =", start)
            if start == -1:
                continue
            end = start + len(fragment)

            overlaps = False
            for colored_segment in colored_segments:
                if start >= colored_segment.end or colored_segment.start >= end:
                    continue
                overlaps = True
                break

            if overlaps:
                # print("start =", start, "end =", end, "overlaps")
                continue

            # print("start =", start, "end =", end, "is ok")

            # if [cs for cs in colored_segments if cd.]
            if color is None:
                color = colors[index_color]
                index_color += 1
                if index_color == len(colors):
                    index_color = 0
            colored_segments.append(ColoredSegment(start=start, end=end, color=color))

        feature_values.append(FeatureValue(id=feature.id, label=label, value=value, color=color))

    # HIGHLIGHT TEXT
    highlighted_text = text
    colored_segments.sort(key=lambda _colored_segment: _colored_segment.start, reverse=True)
    for colored_segment in colored_segments:
        # print(colored_segment.start, colored_segment.end, colored_segment.color)
        if colored_segment.color is not None:
            highlighted_text = (highlighted_text[:colored_segment.start]
                                + f"<span style='background-color: {colored_segment.color}'>"
                                + highlighted_text[colored_segment.start:colored_segment.end]
                                + "</span>"
                                + highlighted_text[colored_segment.end:])

    # highlighted_text = "<b>" + highlighted_text + "</b>"
    highlighted_text = f'<table border="1" cellpadding="10"><tr><td bgcolor="#F0F2F6">{highlighted_text}</td></tr></table>'

    table = "<table cellpadding='10'>"
    for feature_value in feature_values:
        table += f"<tr><td bgcolor=#F0F2F6>{feature_value.label}</td><td bgcolor={feature_value.color}>{feature_value.value}</td></tr>"
    table += "</table>"

    highlighted_text += "<br>"
    highlighted_text += table

    return highlighted_text.replace("\n", "<br>")  # self


def hilite(label: str) -> str:
    return f'<label style="font-weight: bold;">{label}</label>'


def hilite_blue(text: str) -> str:
    return f'<p style="font-weight: bold; color: blue;">{text}</p>'


def render_email(email: Optional[Email]) -> str:
    if email is None:
        return None
    s = hilite("From:&nbsp;") + email.from_email_address + "<br>"
    s += hilite("To:&nbsp;") + email.to_email_address + "<br>"
    s += hilite("Subject:&nbsp;") + email.subject + "<br><br>"
    s += email.body
    return s


standard_table_style = """<style>
      table, th, td {
        border: 1px solid #000;
        border-collapse: collapse;   /* makes adjacent borders appear as one */
      }
      th {
        background: #F0F2F6;
      }
    </style>"""

