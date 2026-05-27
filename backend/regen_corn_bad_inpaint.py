"""
Regenerate `corn-final-bad@2x.png` as a TRUE pixel-aligned overlay of the
GOOD corn. Goal: identical composition / camera / leaves / sky / kernel
positions — the ONLY visible difference must be:
  - a small black-smut cluster (~thumbnail-size) at the very TIP of the cob
  - a few (~5-10) shrivelled brown kernels scattered in the upper quarter
Everything below the upper quarter of the cob MUST be IDENTICAL to the
input pixel-for-pixel: same kernels, same leaves, same husk, same sky,
same lighting, same blur.
"""
import asyncio
import base64
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

load_dotenv("/app/backend/.env")

GOOD_PATH = Path("/app/frontend/public/corn-final-good@2x.png")
BAD_OUT = Path("/app/frontend/public/corn-final-bad@2x.png")

EDIT_PROMPT = (
    "You will edit ONE photograph (attached). This is an in-painting edit, "
    "NOT a re-generation. You MUST output a pixel-identical copy of the "
    "input EXCEPT for a tiny, well-localised area at the very tip of the "
    "corn cob. Do NOT change camera angle, framing, composition, lighting, "
    "depth of field, kernel pattern, leaves position, husk position, sky, "
    "background blur, or any color in the lower 80% of the image.\n"
    "\n"
    "WHAT TO PAINT IN (and ONLY this):\n"
    "  1) At the very TIP of the cob (the topmost ~6-8% of the cob's length, "
    "     where the silk emerges), paint a small irregular cluster of "
    "     diseased kernels: charcoal-black / dark-purple corn smut bumps, "
    "     covering an area roughly the size of a thumbnail. The cluster "
    "     must follow the kernel rows of the existing cob — do NOT overflow "
    "     onto the leaves or husk.\n"
    "  2) Just below that cluster (next ~5% of cob length), scatter 5-10 "
    "     individual shrivelled brown-red kernels — only on the cob, only "
    "     on existing kernel positions. Other kernels in that band stay "
    "     bright healthy yellow.\n"
    "\n"
    "WHAT MUST STAY EXACTLY THE SAME (every pixel):\n"
    "  • Lower 80% of the cob — every kernel keeps its exact shape, "
    "    position, and bright yellow-orange color.\n"
    "  • All husk leaves — exact shape, exact vivid green color, exact "
    "    position and curl.\n"
    "  • All background leaves and stalks — exact position, exact green/red "
    "    colors, exact blur.\n"
    "  • Sky — exact same blue gradient.\n"
    "  • Lighting direction, highlights, shadows — exact same.\n"
    "  • Image aspect ratio and pixel dimensions — exact same as input.\n"
    "\n"
    "Think of this as Photoshop healing brush in REVERSE: paint a small "
    "blemish onto the tip, but otherwise the photo is unchanged. The "
    "viewer should feel: 'same corn, same field, same day — just the tip "
    "of the cob got a touch of smut.'\n"
    "\n"
    "Output: PNG at the same dimensions as the input, no text, no border."
)


async def main() -> None:
    api_key = os.environ["EMERGENT_LLM_KEY"]
    print(f"api_key: {api_key[:18]}...")

    good = Image.open(GOOD_PATH).convert("RGB")
    print(f"good: {good.size}")

    buf = BytesIO(); good.save(buf, format="PNG")
    good_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    chat = LlmChat(
        api_key=api_key,
        session_id="corn-bad-inpaint",
        system_message=(
            "You are a top-tier retoucher specialised in pixel-precise "
            "in-painting edits. You NEVER re-compose the image. You only "
            "paint requested elements in the requested localised area. "
            "The rest of the input must come out byte-identical in the output."
        ),
    )
    chat.with_model("gemini", "gemini-3-pro-image-preview").with_params(
        modalities=["image", "text"]
    )

    msg = UserMessage(text=EDIT_PROMPT, file_contents=[ImageContent(good_b64)])
    text, images = await chat.send_message_multimodal_response(msg)
    print(f"text: {(text or '')[:200]!r}")
    print(f"images returned: {len(images) if images else 0}")
    if not images:
        raise RuntimeError("no image returned")

    bad = Image.open(BytesIO(base64.b64decode(images[0]["data"]))).convert("RGB")
    print(f"bad raw: {bad.size}")
    if bad.size != good.size:
        bad = bad.resize(good.size, Image.LANCZOS)
        print(f"bad resized to good: {bad.size}")
    bad.save(BAD_OUT, format="PNG", optimize=True)
    print(f"saved → {BAD_OUT}")


if __name__ == "__main__":
    asyncio.run(main())
