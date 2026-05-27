"""
Generate 6 themed timeline icons for the /about page using Gemini Nano Banana
(via emergentintegrations). Each image follows the same visual language: a
small natural still-life that combines BIOTECH (lab glass, droplets, micro
structure) + a PLANT element relevant to the milestone, on a soft natural
background suitable for a circular crop.

Output: WebP 1024x1024 (center-cropped square) into /app/frontend/public/
        with filenames year-icon-2000..year-icon-2025.webp (replacing existing
        ones). The about page already references these paths, so swapping the
        files is enough — no FE code change required.
"""
import asyncio
import io
import os
from pathlib import Path

from PIL import Image
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

PUBLIC_DIR = Path("/app/frontend/public")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "").strip()

# Each item: (filename, milestone_label, prompt)
ITEMS = [
    (
        "year-icon-2000.webp",
        "2000 — Заснування",
        (
            "Macro studio photograph, square 1:1 composition, gentle natural daylight. "
            "A young green wheat sprout emerging from rich dark Ukrainian chernozem soil, "
            "next to a small clear glass lab beaker holding a single droplet of green "
            "bio-liquid catching the light. Soft cream / beige background, shallow depth "
            "of field, biotechnology meets nature. Symbolic of the FOUNDATION of a "
            "bio-agro company: first lab research and the very first sprout. Highly "
            "detailed, photoreal, warm, optimistic, centered subject, fits perfectly "
            "inside a circular crop."
        ),
    ),
    (
        "year-icon-2005.webp",
        "2005 — Перші препарати",
        (
            "Macro studio photograph, square 1:1 composition, soft diffused light. "
            "Two small white plastic bio-product bottles with green caps standing in a "
            "row, next to a fresh young corn / soy seedling with bright green leaves. "
            "A single golden water droplet runs down a leaf. Soft warm beige "
            "background. Represents FIRST BIO-PRODUCTS / first commercial line of "
            "bioinoculants for cereals and legumes. Photoreal, centered, clean, "
            "modern agricultural biotech aesthetic, designed to look beautiful inside "
            "a circular crop."
        ),
    ),
    (
        "year-icon-2010.webp",
        "2010 — Масштабування виробництва",
        (
            "Photoreal square macro shot, soft cinematic light. A precise row of "
            "three identical bio-fertilizer bottles (white, green label) on a clean "
            "production conveyor surface, with a vibrant green leaf placed on top of "
            "the middle bottle as a living signature. Subtle cold-storage frost on "
            "glass in the background, warm cream / sand surrounding color. Conveys "
            "SCALING PRODUCTION with controlled cold thermologistics. Centered "
            "composition, sharp focus on bottles & leaf, fits inside a circle."
        ),
    ),
    (
        "year-icon-2015.webp",
        "2015 — Міжнародні стандарти",
        (
            "Photoreal square 1:1 macro photograph. A small modern lab Petri dish "
            "with a healthy fresh green clover / soy leaf inside it, sitting on a "
            "white certification document with a subtle golden quality seal partially "
            "visible at the bottom edge. Soft warm beige background, shallow depth of "
            "field, professional. Represents INTERNATIONAL QUALITY STANDARDS — "
            "certification of bio-products, partnerships with agroholdings. Clean, "
            "premium, biotech + plant, centered subject, designed for circular crop."
        ),
    ),
    (
        "year-icon-2020.webp",
        "2020 — Технології та сервіс",
        (
            "Photoreal square 1:1 macro photograph, soft natural light. A young "
            "agronomist's hand (only fingertips visible) gently holding a fresh green "
            "leaf, with subtle holographic digital data overlay — tiny floating "
            "translucent indicators (NDVI dots, leaf health icons) hovering just "
            "above the leaf surface. Soft cream / sage background. Conveys TECHNOLOGY "
            "AND SERVICE — modern agro-consulting, turn-key digital growing "
            "technology. Photoreal, futuristic but warm and natural, centered, fits "
            "circular crop."
        ),
    ),
    (
        "year-icon-2025.webp",
        "2025 — Лідерство в галузі",
        (
            "Photoreal square 1:1 macro photograph, golden hour sunlight. A single "
            "mature, perfectly healthy green corn / wheat ear standing tall and "
            "centered, with a subtle out-of-focus Ukrainian field stretching behind "
            "it. A tiny clear glass bio-droplet on one of the kernels / grains "
            "catches the light. Warm cream / gold tonal palette. Symbolizes "
            "INDUSTRY LEADERSHIP — 5000+ farmers, 350+ thousand hectares, the result "
            "of 25 years of bio-agro technology. Triumphant, warm, premium, centered "
            "composition designed for a circular crop."
        ),
    ),
]


def to_square_webp(raw: bytes, dest: Path, size: int = 1024, quality: int = 88) -> None:
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    # Center-crop to square
    side = min(im.width, im.height)
    left = (im.width - side) // 2
    top = (im.height - side) // 2
    im = im.crop((left, top, left + side, top + side)).resize(
        (size, size), Image.LANCZOS
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, format="WEBP", quality=quality, method=6)


async def gen_one(client: OpenAIImageGeneration, filename: str, label: str, prompt: str) -> bool:
    dest = PUBLIC_DIR / filename
    print(f"[gen] {label} -> {dest.name}")
    try:
        images = await client.generate_images(
            prompt=prompt,
            model="gpt-image-1",
            number_of_images=1,
            quality="high",
        )
        if not images:
            print(f"  ! no images returned for {label}")
            return False
        raw = images[0]
        to_square_webp(raw, dest, size=1024, quality=88)
        print(f"  ok: {dest} ({dest.stat().st_size // 1024} KB)")
        return True
    except Exception as e:
        print(f"  ERROR generating {label}: {e}")
        return False


async def main() -> None:
    if not EMERGENT_LLM_KEY:
        raise SystemExit("EMERGENT_LLM_KEY env var is missing")
    client = OpenAIImageGeneration(api_key=EMERGENT_LLM_KEY)
    successes = 0
    for filename, label, prompt in ITEMS:
        ok = await gen_one(client, filename, label, prompt)
        if ok:
            successes += 1
    print(f"\nDone. {successes}/{len(ITEMS)} icons generated.")


if __name__ == "__main__":
    asyncio.run(main())
