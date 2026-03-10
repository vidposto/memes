"""
Fetches real memes from Reddit (no auth needed — public JSON API).
Subreddits: memes, dankmemes, me_irl, AdviceAnimals, funny
"""

import random
import requests
from pathlib import Path
from src.logger import setup_logger

logger = setup_logger("reddit")

SUBREDDITS = [
    "memes",
    "dankmemes",
    "me_irl",
    "funny",
    "AdviceAnimals",
    "terriblefacebookmemes",
    "wholesomememes",
]

HEADERS = {"User-Agent": "MemeTelegramBot/1.0"}


class RedditFetcher:
    def fetch(self, work_dir: Path) -> dict | None:
        sub = random.choice(SUBREDDITS)
        logger.info(f"Fetching from r/{sub}...")

        try:
            r = requests.get(
                f"https://www.reddit.com/r/{sub}/hot.json?limit=50",
                headers=HEADERS,
                timeout=15,
            )
            r.raise_for_status()
            posts = r.json()["data"]["children"]

            # Filter image posts only
            image_posts = [
                p["data"] for p in posts
                if not p["data"].get("is_video", True)
                and p["data"].get("url", "").lower().endswith((".jpg", ".jpeg", ".png"))
                and not p["data"].get("over_18", False)
                and p["data"].get("score", 0) > 500
            ]

            if not image_posts:
                logger.warning(f"No image posts found in r/{sub}")
                return None

            post  = random.choice(image_posts)
            url   = post["url"]
            title = post["title"]
            score = post["score"]

            logger.info(f"Found: '{title}' (score: {score})")

            # Download image
            dest = work_dir / "meme.jpg"
            resp = requests.get(url, timeout=20, stream=True, headers=HEADERS)
            resp.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)

            logger.info(f"Reddit meme downloaded ✓")
            return {
                "meme_path": dest,
                "topic":     sub,
                "caption":   f"😂 {title[:200]}",
                "source":    f"r/{sub}",
            }

        except Exception as e:
            logger.warning(f"Reddit fetch failed: {e}")
            return None
