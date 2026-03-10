"""
Generates a meme image using:
- Groq AI for funny caption
- Pexels/Pixabay/Unsplash for background image
- Pillow to draw text on image
"""

import os
import re
import json
import random
import requests
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from groq import Groq
from src.logger import setup_logger

logger = setup_logger("meme_gen")

W, H = 1080, 1080

MEME_TOPICS = [
    "monday morning struggle",
    "programmer life",
    "when you finally fix the bug",
    "gym motivation fails",
    "adulting problems",
    "online meetings",
    "eating healthy vs junk food",
    "sleeping late",
    "social anxiety",
    "coffee addiction",
    "student life",
    "working from home",
    "checking phone every 5 minutes",
    "overthinking everything",
    "when the wifi goes down",
    "pretending to be busy",
    "waiting for the weekend",
    "trying to save money",
]

SYSTEM_PROMPT = """You are a hilarious meme writer. 
Write short, punchy, relatable English meme text.
Always respond with valid JSON only."""


def _load_font(size: int):
    paths = [
        "/run/current-system/sw/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


class MemeGenerator:
    def __init__(self):
        self.client   = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.pexels   = os.environ.get("PEXELS_API_KEY", "")
        self.pixabay  = os.environ.get("PIXABAY_API_KEY", "")
        self.unsplash = os.environ.get("UNSPLASH_ACCESS_KEY", "")

    def generate(self, work_dir: Path) -> dict:
        topic = random.choice(MEME_TOPICS)
        logger.info(f"Meme topic: {topic}")

        # Step 1: Generate meme text with Groq
        content = self._generate_text(topic)
        logger.info(f"Top text: {content['top_text']}")
        logger.info(f"Bottom text: {content['bottom_text']}")

        # Step 2: Fetch background image
        img_path = work_dir / "bg.jpg"
        self._fetch_image(content["image_keyword"], img_path)

        # Step 3: Draw meme
        meme_path = work_dir / "meme.jpg"
        self._draw_meme(img_path, content["top_text"], content["bottom_text"], meme_path)

        return {
            "meme_path": meme_path,
            "topic":     topic,
            "caption":   content["caption"],
            "source":    "AI Generated",
        }

    def _generate_text(self, topic: str) -> dict:
        prompt = f"""Create a funny relatable meme about: "{topic}"

Return ONLY this JSON:
{{
  "top_text": "Short setup text (max 8 words, ALL CAPS)",
  "bottom_text": "Funny punchline (max 8 words, ALL CAPS)",
  "image_keyword": "specific photo search term that fits the meme visually",
  "caption": "Short funny Telegram caption with emojis, max 100 chars"
}}"""

        res = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=1.0,
            max_tokens=300,
        )
        raw = res.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"```\s*$", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", raw)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            raw = match.group(0)
        return json.loads(raw)

    def _fetch_image(self, keyword: str, dest: Path):
        sources = [self._pexels, self._pixabay, self._unsplash, self._picsum]
        random.shuffle(sources[:3])
        sources.append(self._picsum)

        for source in sources:
            url = source(keyword)
            if url and self._download(url, dest):
                logger.info(f"Image fetched: {keyword}")
                return
        raise RuntimeError("All image sources failed")

    def _pexels(self, q: str):
        if not self.pexels:
            return None
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": self.pexels},
                params={"query": q, "per_page": 10, "orientation": "square"},
                timeout=10,
            )
            r.raise_for_status()
            photos = r.json().get("photos", [])
            return random.choice(photos)["src"]["large"] if photos else None
        except Exception as e:
            logger.warning(f"Pexels: {e}")
            return None

    def _pixabay(self, q: str):
        if not self.pixabay:
            return None
        try:
            r = requests.get(
                "https://pixabay.com/api/",
                params={"key": self.pixabay, "q": q, "image_type": "photo",
                        "per_page": 10, "safesearch": "true"},
                timeout=10,
            )
            r.raise_for_status()
            hits = r.json().get("hits", [])
            return random.choice(hits)["largeImageURL"] if hits else None
        except Exception as e:
            logger.warning(f"Pixabay: {e}")
            return None

    def _unsplash(self, q: str):
        if not self.unsplash:
            return None
        try:
            r = requests.get(
                "https://api.unsplash.com/search/photos",
                headers={"Authorization": f"Client-ID {self.unsplash}"},
                params={"query": q, "per_page": 10},
                timeout=10,
            )
            r.raise_for_status()
            results = r.json().get("results", [])
            return random.choice(results)["urls"]["regular"] if results else None
        except Exception as e:
            logger.warning(f"Unsplash: {e}")
            return None

    def _picsum(self, q: str):
        return f"https://picsum.photos/seed/{random.randint(1,9999)}/1080/1080"

    def _download(self, url: str, dest: Path) -> bool:
        try:
            r = requests.get(url, timeout=20, stream=True)
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            return True
        except Exception as e:
            logger.warning(f"Download failed: {e}")
            return False

    def _draw_meme(self, img_path: Path, top: str, bottom: str, out: Path):
        img = Image.open(img_path).convert("RGB")

        # Crop to square
        iw, ih = img.size
        size = min(iw, ih)
        img = img.crop(((iw-size)//2, (ih-size)//2, (iw+size)//2, (ih+size)//2))
        img = img.resize((W, H), Image.LANCZOS)

        # Darken slightly for text readability
        img = ImageEnhance.Brightness(img).enhance(0.75)

        draw = ImageDraw.Draw(img)

        # Draw top text
        self._draw_meme_text(draw, top, position="top")

        # Draw bottom text
        self._draw_meme_text(draw, bottom, position="bottom")

        img.save(str(out), "JPEG", quality=92)
        logger.info("Meme drawn ✓")

    def _draw_meme_text(self, draw: ImageDraw.Draw, text: str, position: str):
        font_size = 90
        font = _load_font(font_size)

        # Word wrap
        words = text.split()
        lines = []
        line  = ""
        dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        for word in words:
            test = f"{line} {word}".strip()
            bbox = dummy.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= W - 60:
                line = test
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)

        line_h  = font_size + 15
        total_h = len(lines) * line_h

        if position == "top":
            start_y = 30
        else:
            start_y = H - total_h - 30

        for i, ln in enumerate(lines):
            bbox = draw.textbbox((0, 0), ln, font=font)
            lw   = bbox[2] - bbox[0]
            x    = (W - lw) // 2
            y    = start_y + i * line_h

            # Black outline
            for dx, dy in [(-3,-3),(3,-3),(-3,3),(3,3),(0,4),(4,0),(-4,0),(0,-4)]:
                draw.text((x+dx, y+dy), ln, font=font, fill=(0, 0, 0))

            # White text
            draw.text((x, y), ln, font=font, fill=(255, 255, 255))
