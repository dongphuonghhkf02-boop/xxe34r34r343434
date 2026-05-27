"""
One-shot script: takes /app/frontend/public/corn-healthy@2x.png as reference
and asks Gemini Nano Banana to produce a DAMAGED / DISEASED variation of the
SAME cob in the SAME pose / framing / aspect ratio, so the two images can be
wipe-blended in a before/after slider without misalignment.

Outputs to /app/frontend/public/corn-bad-gen@2x.png
"""
import asyncio
import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

load_dotenv("/app/backend/.env")

REF_PATH = Path("/app/frontend/public/corn-healthy@2x.png")
OUT_PATH = Path("/app/frontend/public/corn-bad-gen@2x.png")

EDIT_PROMPT = (
    "Take the corn cob in the reference image and produce a variation where "
    "the SAME cob, in EXACTLY the SAME pose, angle, position, scale and crop, "
    "now looks diseased and rotten: "
    "the top third of the cob has black moldy / fungus-infected kernels "
    "(some bumpy charcoal-black smut, some shriveled dark purple), "
    "the rest of the kernels are dull dark red, brownish-orange, "
    "shriveled and uneven, with visible mold strings between rows; "
    "the husk leaves are dry, withered, yellow-brown instead of green; "
    "the background changes from green corn field to dry brown stubble "
    "with slight motion-blur (same blur level / DOF). "
    "Lighting direction and shadow exactly match the source. "
    "OUTPUT MUST: keep the cob in the IDENTICAL position within the frame "
    "as the source, identical aspect ratio (portrait), identical crop. "
    "Photorealistic, high-quality macro photography style. "
    "DO NOT shift, rotate, or rescale the cob."
)


async def main() -> None:
    api_key = os.environ["EMERGENT_LLM_KEY"]
    assert REF_PATH.exists(), f"reference image not found: {REF_PATH}"

    with REF_PATH.open("rb") as f:
        ref_b64 = base64.b64encode(f.read()).decode("utf-8")

    chat = LlmChat(
        api_key=api_key,
        session_id="corn-pair-gen-1",
        system_message=(
            "You are a high-end retouching artist working on a before/after "
            "agricultural visualization. You preserve geometry pixel-perfectly."
        ),
    )
    chat.with_model("gemini", "gemini-3.1-flash-image-preview").with_params(
        modalities=["image", "text"]
    )

    msg = UserMessage(
        text=EDIT_PROMPT,
        file_contents=[ImageContent(ref_b64)],
    )

    text, images = await chat.send_message_multimodal_response(msg)
    print(f"[gen] text response (first 200 chars): {(text or '')[:200]!r}")
    print(f"[gen] images returned: {len(images) if images else 0}")

    if not images:
        raise RuntimeError("Nano Banana returned no images")

    img = images[0]
    print(f"[gen] mime={img.get('mime_type')}")
    data_bytes = base64.b64decode(img["data"])
    OUT_PATH.write_bytes(data_bytes)
    print(f"[gen] saved → {OUT_PATH} ({len(data_bytes)} bytes)")


if __name__ == "__main__":
    asyncio.run(main())
