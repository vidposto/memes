import os
import requests
from pathlib import Path
from src.logger import setup_logger

logger = setup_logger("telegram")

BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")
API_BASE   = f"https://api.telegram.org/bot{BOT_TOKEN}"


class TelegramPoster:
    def post_photo(self, image_path: Path, caption: str) -> str:
        logger.info("Posting meme to Telegram...")
        with open(image_path, "rb") as f:
            r = requests.post(
                f"{API_BASE}/sendPhoto",
                data={
                    "chat_id":    CHANNEL_ID,
                    "caption":    caption[:1024],
                    "parse_mode": "HTML",
                },
                files={"photo": f},
                timeout=30,
            )
        r.raise_for_status()
        msg_id = r.json()["result"]["message_id"]
        logger.info(f"Meme posted ✓ message_id={msg_id}")
        return str(msg_id)
