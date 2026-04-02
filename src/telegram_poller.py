from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from telethon import TelegramClient

from config import settings, channels_config, rules_config, schedule_config
from matcher import match_rule
from router import route_alert
from state_store import (
    get_last_seen_id,
    load_state,
    save_state,
    set_last_seen_id,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def build_client() -> TelegramClient:
    if settings.telegram_api_id == 0:
        raise ValueError("TELEGRAM_API_ID is empty or invalid")

    if not settings.telegram_api_hash:
        raise ValueError("TELEGRAM_API_HASH is empty")

    return TelegramClient(
        settings.telegram_session_name,
        settings.telegram_api_id,
        settings.telegram_api_hash,
    )


def get_enabled_channels() -> list[dict[str, Any]]:
    return [channel for channel in channels_config if channel.get("enabled", True)]


def find_rule_by_name(rule_name: str) -> dict[str, Any] | None:
    for rule in rules_config:
        if rule.get("name") == rule_name:
            return rule
    return None


def get_poll_interval_seconds() -> int:
    now = datetime.now().time()

    day_cfg = schedule_config.get("day", {})
    night_cfg = schedule_config.get("night", {})

    day_start = int(str(day_cfg.get("start", "07:00")).split(":")[0])
    day_end = int(str(day_cfg.get("end", "23:00")).split(":")[0])

    if day_start <= now.hour < day_end:
        return int(day_cfg.get("interval_seconds", 240))

    return int(night_cfg.get("interval_seconds", 60))


async def initialize_last_seen_ids(client: TelegramClient, state: dict[str, Any], channels: list[dict[str, Any]]) -> None:
    for channel in channels:
        username = channel.get("username", "").strip()
        if not username:
            continue

        current_last_seen_id = get_last_seen_id(state, username)
        if current_last_seen_id > 0:
            continue

        messages = await client.get_messages(username, limit=1)
        if messages:
            set_last_seen_id(state, username, messages[0].id)
            logger.info("Initialized last_seen_id | channel=%s | message_id=%s", username, messages[0].id)
        else:
            set_last_seen_id(state, username, 0)

    save_state(state)


async def process_channel(client: TelegramClient, state: dict[str, Any], channel_config: dict[str, Any]) -> None:
    username = channel_config.get("username", "").strip()
    if not username:
        return

    rule_names = channel_config.get("rules", [])
    target_names = channel_config.get("targets", [])

    messages = await client.get_messages(username, limit=5)
    if not messages:
        logger.info("No messages found | channel=%s", username)
        return

    messages = list(reversed(messages))
    last_seen_id = get_last_seen_id(state, username)

    for message in messages:
        if not message or not message.id:
            continue

        if message.id <= last_seen_id:
            continue

        text = message.raw_text or ""
        logger.info("Checking message | channel=%s | message_id=%s | text=%s", username, message.id, text[:300])

        for rule_name in rule_names:
            rule_config = find_rule_by_name(rule_name)
            if not rule_config:
                logger.warning("Rule not found | rule=%s", rule_name)
                continue

            match_result = match_rule(text, rule_config)

            if match_result["matched"]:
                logger.info(
                    "MATCH FOUND | channel=%s | message_id=%s | rule=%s | result=%s",
                    username,
                    message.id,
                    rule_name,
                    match_result,
                )
                route_alert(
                    state=state,
                    target_names=target_names,
                    rule_config=rule_config,
                    context={
                        "channel": username,
                        "message_id": message.id,
                        "match_result": match_result,
                    },
                )
                save_state(state)
            else:
                logger.info(
                    "No match | channel=%s | message_id=%s | rule=%s | reason=%s",
                    username,
                    message.id,
                    rule_name,
                    match_result["reason"],
                )

        set_last_seen_id(state, username, message.id)
        save_state(state)


async def start_poller() -> None:
    client = build_client()

    await client.start(phone=settings.telegram_phone)
    me = await client.get_me()
    logger.info("Logged in as: %s", getattr(me, "username", None) or me.id)

    enabled_channels = get_enabled_channels()
    if not enabled_channels:
        raise ValueError("No enabled channels configured in config/channels.yaml")

    logger.info("Polling channels: %s", [channel.get("username") for channel in enabled_channels])

    state = load_state()
    await initialize_last_seen_ids(client, state, enabled_channels)

    while True:
        interval = get_poll_interval_seconds()
        logger.info("Polling iteration started | interval_seconds=%s", interval)

        for channel in enabled_channels:
            try:
                await process_channel(client, state, channel)
            except Exception as e:
                logger.exception("Failed to process channel=%s | error=%s", channel.get("username"), e)

        logger.info("Sleeping for %s seconds", interval)
        await asyncio.sleep(interval)