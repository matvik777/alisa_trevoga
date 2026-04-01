from typing import Any


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def remove_ignored_lines(text: str, ignore_lines: list[str]) -> str:
    cleaned_lines = []

    for line in text.splitlines():
        normalized_line = normalize_text(line)
        should_ignore = False

        for ignore_line in ignore_lines:
            if normalized_line == normalize_text(ignore_line):
                should_ignore = True
                break

        if not should_ignore:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def contains_any_phrase(text: str, phrases: list[str]) -> bool:
    normalized_text = normalize_text(text)

    for phrase in phrases:
        normalized_phrase = normalize_text(phrase)
        if normalized_phrase and normalized_phrase in normalized_text:
            return True

    return False


def prepare_text(text: str, channel_config: dict[str, Any]) -> str:
    ignore_lines = channel_config.get("ignore_lines", [])
    text = remove_ignored_lines(text, ignore_lines)
    return normalize_text(text)


def match_channel_rule(text: str, channel_config: dict[str, Any]) -> bool:
    prepared_text = prepare_text(text, channel_config)

    important_geo = channel_config.get("important_geo", [])
    trigger_phrases = channel_config.get("trigger_phrases", [])
    exclude_phrases = channel_config.get("exclude_phrases", [])

    if not prepared_text:
        return False

    # Сначала жестко отсекаем стоп-фразы
    if exclude_phrases and contains_any_phrase(prepared_text, exclude_phrases):
        return False

    # Обязательно должно быть нужное гео
    if not important_geo or not contains_any_phrase(prepared_text, important_geo):
        return False

    # Обязательно должен быть триггер угрозы
    if not trigger_phrases or not contains_any_phrase(prepared_text, trigger_phrases):
        return False

    return True