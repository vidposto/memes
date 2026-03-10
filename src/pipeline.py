import random
from datetime import datetime
from pathlib import Path
from src.logger import setup_logger
from src.meme_generator import MemeGenerator
from src.reddit_fetcher import RedditFetcher
from src.telegram_poster import TelegramPoster
from src.cleanup import cleanup

logger = setup_logger("pipeline")


class Pipeline:
    def __init__(self):
        self.work_dir = Path("output")
        self.work_dir.mkdir(exist_ok=True)
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def run(self) -> dict:
        work = self.work_dir / self.run_id
        work.mkdir(exist_ok=True)

        # 50/50 chance: AI generated vs Reddit
        source_type = random.choice(["ai", "reddit"])
        logger.info(f"🎲 Source: {source_type.upper()}")

        result = None
        try:
            if source_type == "reddit":
                result = RedditFetcher().fetch(work)
                if not result:
                    logger.warning("Reddit failed — falling back to AI")
                    source_type = "ai"

            if source_type == "ai" or result is None:
                result = MemeGenerator().generate(work)

            # Post to Telegram
            TelegramPoster().post_photo(
                image_path=result["meme_path"],
                caption=result["caption"],
            )

            cleanup([work])
            return {
                "success": True,
                "source":  result["source"],
                "topic":   result["topic"],
            }

        except Exception as e:
            logger.exception(f"Pipeline error: {e}")
            cleanup([work])
            return {"success": False, "error": str(e)}
