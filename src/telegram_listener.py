import logging
from typing import Any

from telethon import TelegramClient, events, connection

from alisa_api import run_scenario, AlisaAPIError
from config import settings, channels_config
from matcher import match_channel_rule
from mtproxy_loader import load_mtproxies

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def get_enabled_channels() -> list[dict[str, Any]]:
    return [channel for channel in channels_config if channel.get("enabled", True)]


def get_channel_usernames(enabled_channels: list[dict[str, Any]]) -> list[str]:
    usernames = []

    for channel in enabled_channels:
        username = channel.get("username", "").strip()
        if username:
            usernames.append(username)

    return usernames


def find_channel_config_by_username(
    username: str,
    enabled_channels: list[dict[str, Any]],
) -> dict[str, Any] | None:
    username = username.lower().strip()

    for channel in enabled_channels:
        channel_username = channel.get("username", "").lower().strip()
        if channel_username == username:
            return channel

    return None


async def build_working_client() -> TelegramClient:
    if settings.telegram_api_id == 0:
        raise ValueError("TELEGRAM_API_ID is empty or invalid")

    if not settings.telegram_api_hash:
        raise ValueError("TELEGRAM_API_HASH is empty")

    proxies = load_mtproxies(limit=8)
    if not proxies:
        raise ValueError("No MTProto proxies loaded")

    last_error: Exception | None = None

    for index, (host, port, secret) in enumerate(proxies, start=1):
        logger.info("Trying MTProto proxy %s: %s:%s", index, host, port)

        client = TelegramClient(
            settings.telegram_session_name,
            settings.telegram_api_id,
            settings.telegram_api_hash,
            connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
            proxy=(host, port, secret),
        )

        try:
            await client.start(phone=settings.telegram_phone)
            me = await client.get_me()
            logger.info(
                "Connected with proxy %s | user=%s",
                index,
                getattr(me, "username", None) or me.id,
            )
            return client
        except Exception as e:
            last_error = e
            logger.warning(
                "Proxy %s failed | %s:%s | error=%s",
                index,
                host,
                port,
                e,
            )
            try:
                await client.disconnect()
            except Exception:
                pass

    raise RuntimeError(f"All MTProto proxies failed. Last error: {last_error}")


async def start_listener() -> None:
    client = await build_working_client()

    enabled_channels = get_enabled_channels()
    channel_usernames = get_channel_usernames(enabled_channels)

    if not channel_usernames:
        raise ValueError("No enabled channels configured in config/channels.yaml")

    logger.info("Listening only to channels: %s", channel_usernames)

    @client.on(events.NewMessage(chats=channel_usernames))
    async def handle_new_message(event):
        chat = await event.get_chat()
        chat_title = (
            getattr(chat, "title", None)
            or getattr(chat, "username", None)
            or str(getattr(chat, "id", "unknown"))
        )
        chat_username = getattr(chat, "username", "") or ""
        text = event.raw_text or ""

        logger.info("New message | chat=%s | text=%s", chat_title, text[:300])

        channel_config = find_channel_config_by_username(chat_username, enabled_channels)
        if not channel_config:
            logger.warning("No config found for chat username=%s", chat_username)
            return

        matched = match_channel_rule(text, channel_config)

        if not matched:
            logger.info(
                "No match | channel=%s | channel_name=%s",
                chat_title,
                channel_config.get("name"),
            )
            return

        logger.info(
            "MATCH FOUND | channel=%s | channel_name=%s",
            chat_title,
            channel_config.get("name"),
        )

        if not channel_config.get("trigger_scenario", False):
            logger.info(
                "Scenario trigger disabled | channel=%s | channel_name=%s",
                chat_title,
                channel_config.get("name"),
            )
            return

        try:
            result = run_scenario()
            logger.info(
                "Scenario started | channel=%s | channel_name=%s | result=%s",
                chat_title,
                channel_config.get("name"),
                result,
            )
        except AlisaAPIError as e:
            logger.error(
                "Failed to start scenario | channel=%s | channel_name=%s | error=%s",
                chat_title,
                channel_config.get("name"),
                e,
            )

    logger.info("Telegram listener started")
    await client.run_until_disconnected()