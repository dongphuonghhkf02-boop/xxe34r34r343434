"""
v2 generator: keep cob position PIXEL-aligned with the source good image.

Approach:
  1. Use the higher-quality gemini-3-pro-image-preview model
  2. Tell it the output MUST be at the same pixel resolution as the source and
     the cob must be at the same column / scale / angle pixel-for-pixel.
  3. Resize result to exact source dimensions via PIL (safety net).

Output: /app/frontend/public/corn-bad-gen@2x.png  (replaces v1)
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

REF_PATH = Path("/app/frontend/public/corn-healthy@2x.png")
OUT_PATH = Path("/app/frontend/public/corn-bad-gen@2x.png")

EDIT_PROMPT = (
    "Edit the attached photograph. Keep EVERY pixel of the cob's geometry "
    "exactly where it is — same column, same row, same scale, same rotation, "
    "same silhouette. Do not rescale, do not re-crop, do not shift. "
    "Imagine you are applying digital rot/disease to the same physical cob:\n"
    " • Top third of the cob → covered in bumpy charcoal-black corn smut "
    "(Ustilago maydis) and dark purple shriveled kernels.\n"
    " • Middle third → dull dark-red and brownish-orange kernels, some "
    "shriveled, some collapsed, mold filaments between rows.\n"
    " • Bottom third → still rotten, brown-red, dehydrated, no green tint.\n"
    " • Husk leaves around the cob (currently green) → dry yellow-brown, "
    "withered, curled at edges. SAME shape and SAME position as in source.\n"
    " • Out-of-focus background (currently green corn field) → blurred "
    "dry-brown stubble with same depth-of-field/blur level.\n"
    "Lighting direction, shadow positions, depth-of-field, focal length "
    "must remain IDENTICAL. The cob silhouette must align pixel-for-pixel "
    "with the source — anyone overlaying the two images must see the cob "
    "in the same spot. Photo-realistic macro photography, same camera. "
    "Output a portrait image with the EXACT same aspect ratio as the input."
)


async def main() -> None:
    api_key = os.environ["EMERGENT_LLM_KEY"]
    assert REF_PATH.exists(), f"missing reference image: {REF_PATH}"

    src = Image.open(REF_PATH).convert("RGB")
    src_w, src_h = src.size
    print(f"[gen] reference size: {src_w}x{src_h}")

    with REF_PATH.open("rb") as f:
        ref_b64 = base64.b64encode(f.read()).decode("utf-8")

    chat = LlmChat(
        api_key=api_key,
        session_id="corn-pair-gen-v2",
        system_message=(
            "You are a top-tier retoucher. You preserve geometry and "
            "composition pixel-perfectly when applying photo edits."
        ),
    )
    chat.with_model(
        "gemini", "gemini-3-pro-image-preview"
    ).with_params(modalities=["image", "text"])

    msg = UserMessage(text=EDIT_PROMPT, file_contents=[ImageContent(ref_b64)])
    text, images = await chat.send_message_multimodal_response(msg)
    print(f"[gen] text response (first 200): {(text or '')[:200]!r}")
    print(f"[gen] images returned: {len(images) if images else 0}")
    if not images:
        raise RuntimeError("no images returned")

    img_bytes = base64.b64decode(images[0]["data"])
    gen = Image.open(BytesIO(img_bytes)).convert("RGB")
    print(f"[gen] generated size: {gen.size}")

    # Resize to EXACTLY source dimensions to guarantee pixel alignment.
    if gen.size != (src_w, src_h):
        gen = gen.resize((src_w, src_h), Image.LANCZOS)
        print(f"[gen] resized to source: {gen.size}")

    gen.save(OUT_PATH, format="PNG", optimize=True)
    print(f"[gen] saved → {OUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
