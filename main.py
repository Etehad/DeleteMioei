import asyncio
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import RPCError


# =========================
# Environment Variables
# =========================

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
TELEGRAM_SESSION = os.environ["TELEGRAM_SESSION"]
TARGET_CHAT_ID = int(os.environ["TARGET_CHAT_ID"])

# Port provided by hosting platform
PORT = int(os.environ.get("PORT", 10000))


# =========================
# Telegram Settings
# =========================

SPECIAL_BOT_ID = 8299996037

EXACT_MESSAGES = {
    "مع",
    "میو",
    "میک",
    "پیشی",
    "گربه",
    "رولت میویی",
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


# =========================
# Logging
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


# =========================
# Telegram Client
# =========================

client = TelegramClient(
    StringSession(TELEGRAM_SESSION),
    API_ID,
    API_HASH,
)


# =========================
# Health / HTTP Server
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/":
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )
            self.end_headers()

            self.wfile.write(
                b"Telegram bot is running."
            )

        elif self.path == "/health":
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )
            self.end_headers()

            self.wfile.write(
                b"OK"
            )

        else:
            self.send_response(404)
            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8"
            )
            self.end_headers()

            self.wfile.write(
                b"Not Found"
            )

    def log_message(self, format, *args):
        # Disable HTTP access logs
        return


def start_web_server():

    try:
        server = ThreadingHTTPServer(
            ("0.0.0.0", PORT),
            HealthHandler
        )

        logging.info(
            "HTTP server started on 0.0.0.0:%s",
            PORT
        )

        server.serve_forever()

    except Exception:
        logging.exception(
            "HTTP server crashed."
        )


# =========================
# Delete Message Later
# =========================

async def delete_later(
    chat_id: int,
    message_id: int,
    delay_seconds: int
):

    try:

        await asyncio.sleep(delay_seconds)

        await client.delete_messages(
            chat_id,
            message_id
        )

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

        logging.exception(
            "Unexpected error deleting message %s",
            message_id
        )


# =========================
# Telegram Message Handler
# =========================

@client.on(events.NewMessage(chats=TARGET_CHAT_ID))
async def message_handler(event):

    message = event.message

    text = message.raw_text or ""
    normalized = text.strip()

    # -------------------------
    # Content rules
    # -------------------------

    if (
        normalized in EXACT_MESSAGES
        or any(
            phrase in text
            for phrase in CONTAINS_MESSAGES
        )
    ):
        delay = 600
        reason = "content rule"

    else:

        # -------------------------
        # Special bot rule
        # -------------------------

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
        delete_later(
            TARGET_CHAT_ID,
            message.id,
            delay
        )
    )


# =========================
# Main
# =========================

async def main():

    try:

        logging.info("Connecting to Telegram...")

        await client.start()

        me = await client.get_me()

        logging.info(
            "Logged in as %s (id=%s)",
            getattr(me, "username", None)
            or getattr(me, "first_name", None),
            me.id,
        )

        logging.info(
            "Watching group %s",
            TARGET_CHAT_ID
        )

        logging.info(
            "HTTP port = %s",
            PORT
        )

        logging.info(
            "Telegram client is running."
        )

        await client.run_until_disconnected()

    except Exception:

        logging.exception(
            "Telegram client crashed."
        )

        raise


# =========================
# Start Application
# =========================

if __name__ == "__main__":

    logging.info(
        "Starting Telegram application..."
    )

    # Start HTTP server in background thread
    web_thread = threading.Thread(
        target=start_web_server,
        daemon=True
    )

    web_thread.start()

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        logging.info(
            "Stopped manually."
        )

    except Exception:

        logging.exception(
            "Application terminated بسبب خطا."
        )

        raise
