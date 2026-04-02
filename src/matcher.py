from __future__ import annotations

from typing import Any


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def remove_ignored_lines(text: str, ignore_lines: list[str]) -> str:
    cleaned_lines = []

    normalized_ignore_lines = {normalize_text(line) for line in ignore_lines if line.strip()}

    for line in text.splitlines():
        normalized_line = normalize_text(line)
        if normalized_line in normalized_ignore_lines:
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def contains_any_phrase(text: str, phrases: list[str]) -> list[str]:
    matched = []
    normalized_text = normalize_text(text)

    for phrase in phrases:
        normalized_phrase = normalize_text(phrase)
        if normalized_phrase and normalized_phrase in normalized_text:
            matched.append(phrase)

    return matched


def prepare_text(text: str, ignore_lines: list[str]) -> str:
    cleaned = remove_ignored_lines(text, ignore_lines)
    return normalize_text(cleaned)


def match_rule(text: str, rule_config: dict[str, Any]) -> dict[str, Any]:
    ignore_lines = rule_config.get("ignore_lines", [])
    important_geo = rule_config.get("important_geo", [])
    trigger_phrases = rule_config.get("trigger_phrases", [])
    exclude_phrases = rule_config.get("exclude_phrases", [])

    prepared_text = prepare_text(text, ignore_lines)

    if not prepared_text:
        return {
            "matched": False,
            "reason": "empty_text",
            "matched_geo": [],
            "matched_triggers": [],
            "matched_excludes": [],
        }

    matched_excludes = contains_any_phrase(prepared_text, exclude_phrases)
    if matched_excludes:
        return {
            "matched": False,
            "reason": "exclude_phrase",
            "matched_geo": [],
            "matched_triggers": [],
            "matched_excludes": matched_excludes,
        }

    matched_geo = contains_any_phrase(prepared_text, important_geo)
    if not matched_geo:
        return {
            "matched": False,
            "reason": "missing_important_geo",
            "matched_geo": [],
            "matched_triggers": [],
            "matched_excludes": [],
        }

    matched_triggers = contains_any_phrase(prepared_text, trigger_phrases)
    if not matched_triggers:
        return {
            "matched": False,
            "reason": "missing_trigger_phrase",
            "matched_geo": matched_geo,
            "matched_triggers": [],
            "matched_excludes": [],
        }

    return {
        "matched": True,
        "reason": "important_geo_and_trigger_phrase",
        "matched_geo": matched_geo,
        "matched_triggers": matched_triggers,
        "matched_excludes": [],
    }