import asyncio

from telegram_poller import start_poller


def main() -> None:
    asyncio.run(start_poller())


if __name__ == "__main__":
    main()