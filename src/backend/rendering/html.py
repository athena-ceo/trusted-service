from typing import Any, Optional, List

from pydantic import BaseModel

from src.backend.distribution.distribution_email.email2 import Email
from src.backend.rendering.html_localization import html_localizations, SupportedLocale, HTMLLocalization
from src.backend.text_analysis.base_models import Feature, PREFIX_FRAGMENTS
from src.common.logging import print_red

standard_back_ground_color = "#F0F2F6"

standard_table_style = f"""<style>
      table, th, td {'{'}
        border: 1px solid #000;
        border-collapse: collapse;   /* makes adjacent borders appear as one */
      {'}'}
      th {'{'}
        background: {standard_back_ground_color};
      {'}'}
    </style>"""


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


def build_html_highlighted_text_and_features(locale: SupportedLocale, 
                                             text: str,
                                             features: list[Feature],
                                             analysis_result: dict[str, Any]) -> str:
    colors = ["lightblue", "pink", "lightgreen", "cyan", "yellow"]
    index_color = 0
    colored_segments: list[ColoredSegment] = []
    feature_values: list[FeatureValue] = []
    localizations: HTMLLocalization = html_localizations[locale]

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

        # Here, there is at least one fragment for the current feature
        # Let's check that there is at least one that fulfills the two conditions:
        # 1. We find that fragment in the text.
        # Due to hallucination, this is not necessarily the case.
        # For instance, the following has been detected:
        # "the processing‑extension certificate expired on 11 October 2024"
        # while the initial text is:
        # "Mr C’s processing‑extension certificate expired on 11 October 2024"
        # 2. That fragment does not overlap with an already registrerd fragment

        for fragment in fragments["list"]:
            start = text.find(fragment)
            if start == -1:  # condition 1 not met
                print_red(f"Fragment '{fragment}' not found in the original text ...")
                # Trying by capitilizing
                start = text.upper().find(fragment.upper())
                if start == -1:  # condition 1 not met
                    print_red(f"even after comparing uppercase copies")
                    continue
                else:
                    print_red(f"but found after comparing uppercase copies")
            end = start + len(fragment)

            overlaps = False
            for colored_segment in colored_segments:
                if start >= colored_segment.end or colored_segment.start >= end:
                    continue
                overlaps = True
                break

            if overlaps:  # condition 2 not met
                print_red("{start}-{end} overlaps")
                continue

            # if [cs for cs in colored_segments if cd.]
            if color is None:  # First fragment of the feature
                color = colors[index_color]
                index_color += 1
                if index_color == len(colors):
                    index_color = 0
            colored_segments.append(ColoredSegment(start=start, end=end, color=color))

        if color is None:
            color = standard_back_ground_color
        feature_values.append(FeatureValue(id=feature.id, label=label, value=value, color=color))

    # HIGHLIGHT TEXT
    highlighted_text = text
    colored_segments.sort(key=lambda _colored_segment: _colored_segment.start, reverse=True)
    for colored_segment in colored_segments:

        if colored_segment.color is not None:
            highlighted_text = (highlighted_text[:colored_segment.start]
                                + f"<span style='background-color: {colored_segment.color}'>"
                                + highlighted_text[colored_segment.start:colored_segment.end]
                                + "</span>"
                                + highlighted_text[colored_segment.end:])

    # highlighted_text = "<b>" + highlighted_text + "</b>"
    highlighted_text = f'<table border="1" cellpadding="10"><tr><td bgcolor="{standard_back_ground_color}">{highlighted_text}</td></tr></table>'

    table = "<table cellpadding='10'>"
    for feature_value in feature_values:
        value = feature_value.value
        if isinstance(feature_value.value, bool):
            #value: str= html_localizations["en"].label_yes if feature_value.value else html_localizations["en"].label_no
            value: str= localizations.label_yes if feature_value.value else localizations.label_no
        table += f"<tr><td bgcolor=#F0F2F6>{feature_value.label}</td><td bgcolor={feature_value.color}>{value}</td></tr>"
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
