import asyncio

from telegram_listener import start_listener


def main() -> None:
    asyncio.run(start_listener())


if __name__ == "__main__":
    main()