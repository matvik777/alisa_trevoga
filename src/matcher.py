from typing import Any


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def contains_any_keyword(text: str, keywords: list[str]) -> bool:
    normalized_text = normalize_text(text)
    normalized_keywords = [kw.lower().strip() for kw in keywords if kw.strip()]

    return any(keyword in normalized_text for keyword in normalized_keywords)


def match_channel_rule(text: str, channel_config: dict[str, Any]) -> bool:
    keywords = channel_config.get("keywords", [])
    exclude_keywords = channel_config.get("exclude_keywords", [])

    if not keywords:
        return False

    if not contains_any_keyword(text, keywords):
        return False

    if exclude_keywords and contains_any_keyword(text, exclude_keywords):
        return False

    return True