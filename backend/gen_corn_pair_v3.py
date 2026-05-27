"""
Generate a fresh matched pair of cob images where the cob is CENTERED
horizontally in a portrait frame, so the before/after wipe always intersects
the cob regardless of slider position.

Step 1: ask Nano Banana for a healthy corn cob centered in portrait frame.
Step 2: feed step-1 output to Nano Banana and ask for the matching diseased
        version, preserving cob geometry pixel-for-pixel.

Outputs:
  /app/frontend/public/corn-good-final@2x.png
  /app/frontend/public/corn-bad-final@2x.png
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

GOOD_OUT = Path("/app/frontend/public/corn-good-final@2x.png")
BAD_OUT = Path("/app/frontend/public/corn-bad-final@2x.png")

GOOD_PROMPT = (
    "Photorealistic close-up macro photograph of ONE ripe corn cob, oriented "
    "vertically with a slight natural tilt. CRITICAL: the cob must be "
    "horizontally CENTERED in the frame — the cob's axis runs through the "
    "horizontal middle of the image, leaving roughly equal background on the "
    "left and right sides. The cob fills about 60–70% of the frame's height, "
    "extending from near the top of the frame to near the bottom. Healthy "
    "bright golden-yellow plump kernels, glossy, regular rows. Vibrant green "
    "fresh husk leaves curling around the base of the cob (lower 25% of frame). "
    "Soft out-of-focus green corn field as the background on both sides "
    "(shallow depth of field, f/2.8 look). Warm afternoon sunlight from the "
    "upper right. Vertical portrait composition, 3:4 aspect ratio."
)

BAD_PROMPT = (
    "Edit the attached photograph. Keep the cob's geometry pixel-for-pixel: "
    "same horizontal centre column, same vertical extent, same scale, same "
    "tilt, same silhouette. Anyone overlaying the two images must see the cob "
    "in EXACTLY the same spot. Change ONLY the surface appearance:\n"
    " • Top third of the cob → bumpy charcoal-black corn smut (Ustilago "
    "maydis) and dark purple shrivelled kernels.\n"
    " • Middle third → dull dark-red and brownish-orange kernels, some "
    "shrivelled and collapsed, mold filaments between rows.\n"
    " • Bottom third → still rotten, brown-red, dehydrated.\n"
    " • Husk leaves (currently green) → dry yellow-brown, withered, curled "
    "at the edges. SAME shape and SAME position.\n"
    " • Out-of-focus background (currently green corn field) → blurred "
    "dry-brown stubble field with the same depth of field.\n"
    "Lighting direction, shadow positions, focal length, depth of field MUST "
    "remain identical. Output a portrait image with the EXACT same aspect "
    "ratio as the input."
)


async def generate_one(
    *,
    api_key: str,
    session_id: str,
    prompt: str,
    ref_image_b64: str | None = None,
    model: str = "gemini-3-pro-image-preview",
) -> Image.Image:
    chat = LlmChat(
        api_key=api_key,
        session_id=session_id,
        system_message=(
            "You are a top-tier retouching artist. You preserve geometry and "
            "composition pixel-perfectly when applying photo edits."
        ),
    )
    chat.with_model("gemini", model).with_params(modalities=["image", "text"])
    file_contents = [ImageContent(ref_image_b64)] if ref_image_b64 else None
    msg = UserMessage(text=prompt, file_contents=file_contents)
    text, images = await chat.send_message_multimodal_response(msg)
    print(f"  text: {(text or '')[:120]!r}")
    print(f"  images: {len(images) if images else 0}")
    if not images:
        raise RuntimeError("no image returned")
    return Image.open(BytesIO(base64.b64decode(images[0]["data"]))).convert("RGB")


async def main() -> None:
    api_key = os.environ["EMERGENT_LLM_KEY"]

    print("[1/2] generating GOOD cob (cob centred)...")
    good = await generate_one(
        api_key=api_key,
        session_id="corn-pair-good",
        prompt=GOOD_PROMPT,
    )
    print(f"  good raw: {good.size}")
    good.save(GOOD_OUT, format="PNG", optimize=True)
    print(f"  saved → {GOOD_OUT.name}")

    print("[2/2] generating BAD cob from GOOD (same composition)...")
    good_b64 = base64.b64encode(GOOD_OUT.read_bytes()).decode("utf-8")
    bad = await generate_one(
        api_key=api_key,
        session_id="corn-pair-bad",
        prompt=BAD_PROMPT,
        ref_image_b64=good_b64,
    )
    print(f"  bad raw: {bad.size}")
    # If output dim differs, resize to good's exact dim so they align pixel-for-pixel
    if bad.size != good.size:
        bad = bad.resize(good.size, Image.LANCZOS)
        print(f"  bad resized to good size: {bad.size}")
    bad.save(BAD_OUT, format="PNG", optimize=True)
    print(f"  saved → {BAD_OUT.name}")


if __name__ == "__main__":
    asyncio.run(main())
