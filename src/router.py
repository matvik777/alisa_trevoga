from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from alisa_api import run_scenario
from config import targets_config
from state_store import get_last_triggered_at, set_last_triggered_at_now

logger = logging.getLogger(__name__)


def find_target_by_name(target_name: str) -> dict[str, Any] | None:
    for target in targets_config:
        if target.get("name") == target_name:
            return target
    return None


def is_cooldown_active(state: dict[str, Any], rule_name: str, cooldown_minutes: int) -> bool:
    if cooldown_minutes <= 0:
        return False

    last_triggered_at = get_last_triggered_at(state, rule_name)
    if not last_triggered_at:
        return False

    previous = datetime.fromisoformat(last_triggered_at)
    now = datetime.now(timezone.utc)

    delta_seconds = (now - previous).total_seconds()
    return delta_seconds < cooldown_minutes * 60


def route_alert(
    state: dict[str, Any],
    target_names: list[str],
    rule_config: dict[str, Any],
    context: dict[str, Any],
) -> None:
    rule_name = rule_config.get("name", "unknown_rule")
    cooldown_minutes = int(rule_config.get("cooldown_minutes", 0))

    if is_cooldown_active(state, rule_name, cooldown_minutes):
        logger.info(
            "Cooldown active | rule=%s | cooldown_minutes=%s",
            rule_name,
            cooldown_minutes,
        )
        return

    for target_name in target_names:
        target = find_target_by_name(target_name)
        if not target:
            logger.warning("Target not found | target=%s", target_name)
            continue

        if not target.get("enabled", True):
            logger.info("Target disabled | target=%s", target_name)
            continue

        target_type = target.get("type")
        if target_type == "yandex_scenario":
            scenario_id = target.get("scenario_id", "")
            result = run_scenario(scenario_id)
            logger.info(
                "Target executed | target=%s | type=%s | result=%s | context=%s",
                target_name,
                target_type,
                result,
                context,
            )
        else:
            logger.warning("Unsupported target type | target=%s | type=%s", target_name, target_type)

    set_last_triggered_at_now(state, rule_name)