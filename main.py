import asyncio
import logging
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import RPCError

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
TELEGRAM_SESSION = os.environ["TELEGRAM_SESSION"]

TARGET_CHAT_ID = -1001715381518
SPECIAL_BOT_ID = 8299996037

EXACT_MESSAGES = {
    "مع",
    "میو",
    "ماهی",
    "یخچال میویی",
    "میو بانک",
    "بانک میویی",
    "کارخونه میویی",
}

CONTAINS_MESSAGES = (
    "میو پوینت",
    "رفت تو یخچال",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

client = TelegramClient(
    StringSession(TELEGRAM_SESSION),
    API_ID,
    API_HASH,
)


async def delete_later(chat_id: int, message_id: int, delay_seconds: int):
    try:
        await asyncio.sleep(delay_seconds)
        await client.delete_messages(chat_id, message_id)
        logging.info(
            "Deleted message %s in %s after %s seconds",
            message_id,
            chat_id,
            delay_seconds,
        )
    except asyncio.CancelledError:
        raise
    except RPCError as exc:
        logging.warning(
            "Could not delete message %s: %s",
            message_id,
            exc,
        )
    except Exception:
        logging.exception("Unexpected error deleting message %s", message_id)


@client.on(events.NewMessage(chats=TARGET_CHAT_ID))
async def message_handler(event):
    message = event.message
    text = message.raw_text or ""
    normalized = text.strip()

    # First priority: the two content-based rules.
    # These rules apply regardless of whether the sender is a user or bot.
    if normalized in EXACT_MESSAGES or any(
        phrase in text for phrase in CONTAINS_MESSAGES
    ):
        delay = 60
        reason = "content rule"
    else:
        # Only messages not matching the above rules are checked against the bot ID.
        sender_id = event.sender_id
        if sender_id == SPECIAL_BOT_ID:
            delay = 600
            reason = "special bot rule"
        else:
            return

    logging.info(
        "Scheduled deletion: chat=%s message=%s sender=%s delay=%ss (%s)",
        TARGET_CHAT_ID,
        message.id,
        event.sender_id,
        delay,
        reason,
    )

    asyncio.create_task(
        delete_later(TARGET_CHAT_ID, message.id, delay)
    )


async def main():
    await client.start()
    me = await client.get_me()

    logging.info(
        "Logged in as %s (id=%s)",
        getattr(me, "username", None) or getattr(me, "first_name", None),
        me.id,
    )
    logging.info("Watching group %s", TARGET_CHAT_ID)

    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Stopped.")
