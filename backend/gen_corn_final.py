"""
Final corn pair generator (v4):

  1. Take the user-provided reference image (landscape) and CROP it to a
     portrait window with aspect-ratio 290/340 ≈ 0.853 around the corn cob.
     Save as `corn-final-good@2x.png` (overwrites the raw download).
  2. Feed that cropped portrait to Nano Banana and ask for a MATCHING diseased
     version — same composition, same camera, same background geometry,
     only the cob is rotten and the surrounding field is dry. Save as
     `corn-final-bad@2x.png` at the same pixel dimensions.

Outputs:
  /app/frontend/public/corn-final-good@2x.png   (portrait, cropped reference)
  /app/frontend/public/corn-final-bad@2x.png    (portrait, AI-edited)
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

REF_PATH = Path("/app/frontend/public/corn-final-good@2x.png")  # source (landscape)
GOOD_OUT = Path("/app/frontend/public/corn-final-good@2x.png")  # portrait crop
BAD_OUT = Path("/app/frontend/public/corn-final-bad@2x.png")    # AI-edited

# Card aspect requested by the user: 290 × 340 ≈ 0.853
TARGET_ASPECT = 290 / 340

EDIT_PROMPT = (
    "Edit the attached photograph. Keep the cob's geometry pixel-perfectly: "
    "same horizontal position, same vertical extent, same scale, same tilt, "
    "same silhouette. The rest of the image must remain in the SAME "
    "composition — just imagine the field is now drought-stricken and the "
    "cob is diseased instead of healthy.\n"
    " • The cob (currently bright yellow, healthy) → severely diseased:\n"
    "    – Top third: bumpy charcoal-black corn smut (Ustilago maydis) "
    "and dark purple shrivelled kernels.\n"
    "    – Middle third: dull dark-red and brownish-orange kernels, some "
    "shrivelled and collapsed, mold filaments between rows.\n"
    "    – Bottom third: still rotten, brown-red, dehydrated kernels.\n"
    " • Husk leaves wrapped around the cob (currently green) → dry "
    "yellow-brown, withered, edges curling. SAME shape and SAME position.\n"
    " • Tall corn leaves on the sides of the frame (currently vivid green) → "
    "dry pale yellow-brown, drooping, frost-burnt look.\n"
    " • Sky in the background (currently blue) → washed-out hazy beige sky "
    "with smog/dust.\n"
    " • Out-of-focus distant corn rows (currently green) → dry brown stubble.\n"
    " • Soil between rows (currently brown earth) → cracked dry barren earth.\n"
    "Lighting direction, shadow positions, focal length, depth of field MUST "
    "remain identical. Output a portrait image with the EXACT same aspect "
    "ratio and pixel dimensions as the input."
)


def crop_to_portrait_around_cob(img: Image.Image, aspect: float) -> Image.Image:
    """Crop a landscape image to a portrait window with target `aspect`
    (width/height) centred horizontally on the corn cob.

    Heuristic for cob horizontal centre: column with max saturation
    (cob is the most-saturated yellow region).
    """
    import numpy as np

    rgb = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    sat = np.where(mx > 1e-6, (mx - mn) / (mx + 1e-6), 0.0)
    col_score = sat.mean(axis=0)
    thresh = np.quantile(col_score, 0.70)
    mask = col_score >= thresh
    cx = (
        int(round((np.arange(img.width)[mask] * col_score[mask]).sum() / col_score[mask].sum()))
        if mask.any()
        else img.width // 2
    )

    crop_w = int(round(img.height * aspect))
    if crop_w >= img.width:
        return img
    left = max(0, min(img.width - crop_w, cx - crop_w // 2))
    return img.crop((left, 0, left + crop_w, img.height))


async def main() -> None:
    api_key = os.environ["EMERGENT_LLM_KEY"]

    # Re-open the original landscape reference from the saved file
    src = Image.open(REF_PATH).convert("RGB")
    print(f"reference src size: {src.size} aspect={src.width / src.height:.3f}")

    cropped = crop_to_portrait_around_cob(src, TARGET_ASPECT)
    print(f"cropped to portrait: {cropped.size} aspect={cropped.width / cropped.height:.3f}")
    cropped.save(GOOD_OUT, format="PNG", optimize=True)
    print(f"saved good → {GOOD_OUT.name}")

    # Now ask Nano Banana for the diseased variant
    buf = BytesIO()
    cropped.save(buf, format="PNG")
    good_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    chat = LlmChat(
        api_key=api_key,
        session_id="corn-final-bad",
        system_message=(
            "You are a top-tier retouching artist. You preserve composition "
            "and geometry pixel-for-pixel when applying photo edits."
        ),
    )
    chat.with_model("gemini", "gemini-3-pro-image-preview").with_params(
        modalities=["image", "text"]
    )
    msg = UserMessage(text=EDIT_PROMPT, file_contents=[ImageContent(good_b64)])
    text, images = await chat.send_message_multimodal_response(msg)
    print(f"bad text: {(text or '')[:140]!r}")
    print(f"bad images: {len(images) if images else 0}")
    if not images:
        raise RuntimeError("no bad image returned")

    bad = Image.open(BytesIO(base64.b64decode(images[0]["data"]))).convert("RGB")
    print(f"bad raw: {bad.size}")
    if bad.size != cropped.size:
        bad = bad.resize(cropped.size, Image.LANCZOS)
        print(f"bad resized to good: {bad.size}")
    bad.save(BAD_OUT, format="PNG", optimize=True)
    print(f"saved bad → {BAD_OUT.name}")


if __name__ == "__main__":
    asyncio.run(main())
