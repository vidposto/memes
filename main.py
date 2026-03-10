import os
import time
import schedule
from pathlib import Path
from src.pipeline import Pipeline
from src.logger import setup_logger

logger = setup_logger("main")

LOCK_FILE      = Path("/tmp/memebot.lock")
STATE_FILE     = Path("/tmp/memebot_last_run.txt")
INTERVAL_HOURS = 6


def is_locked() -> bool:
    if not LOCK_FILE.exists():
        return False
    if time.time() - LOCK_FILE.stat().st_mtime > 3600:
        LOCK_FILE.unlink()
        return False
    return True


def ran_recently() -> bool:
    if not STATE_FILE.exists():
        return False
    try:
        elapsed = (time.time() - float(STATE_FILE.read_text().strip())) / 3600
        if elapsed < INTERVAL_HOURS:
            logger.info(f"⏳ Last run {elapsed:.1f}h ago — next in {INTERVAL_HOURS - elapsed:.1f}h")
            return True
    except Exception:
        pass
    return False


def run_job():
    if is_locked() or ran_recently():
        return

    LOCK_FILE.write_text(str(os.getpid()))
    logger.info("=" * 50)
    logger.info("😂 Starting Meme Bot job...")
    logger.info("=" * 50)

    try:
        result = Pipeline().run()
        STATE_FILE.write_text(str(time.time()))
        if result["success"]:
            logger.info(f"✅ Meme posted! Source: {result['source']} | Topic: {result['topic']}")
        else:
            logger.error(f"❌ Failed: {result.get('error')}")
    except Exception as e:
        logger.exception(f"💥 Error: {e}")
    finally:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()


if __name__ == "__main__":
    logger.info("🤖 Meme Bot started")
    logger.info(f"⏰ Posts every {INTERVAL_HOURS} hours")
    run_job()
    schedule.every(30).minutes.do(run_job)
    while True:
        schedule.run_pending()
        time.sleep(60)
