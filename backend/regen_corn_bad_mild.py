"""
Regenerate `corn-final-bad@2x.png` with a MUCH MILDER disease state.

User feedback:
  The previous "bad" corn was way too catastrophic — completely rotten cob,
  black smut covering top third, drought-stricken sky, dead leaves. The user
  wants the visual difference to be SUBTLE — just show "chemicals damage life
  a bit more than biologicals", not "apocalypse vs paradise".

Strategy:
  - Keep IDENTICAL geometry / camera / composition as `corn-final-good@2x.png`
    (this is critical for the wipe slider to look pixel-aligned).
  - Multimodal prompt: pass BOTH
      (a) the good corn (as composition base — must preserve)
      (b) the user-provided reference of MILD disease  (as style hint —
          how much damage to apply visually)
  - Describe disease as:
      * cob mostly still healthy yellow-orange
      * only the TOP TIP has a small cluster of dark/black diseased kernels
        (corn smut spots) — like the reference shows
      * a few scattered shrivelled brownish kernels mixed in the upper third
      * husks naturally drier, slightly yellow-tan (end-of-season look)
        but NOT crumbling
      * background stays roughly the same — late-season field, NOT desert
      * sky stays normal, no smog
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
REF_MILD = Path("/tmp/ref_mild.png")  # user-provided "mild disease" reference

EDIT_PROMPT = (
    "I am attaching two images.\n"
    "IMAGE 1 is the base photograph: a healthy corn cob on the stalk, "
    "shot in portrait orientation. You MUST preserve IMAGE 1's exact "
    "composition pixel-for-pixel: same camera angle, same cob position, "
    "same cob silhouette, same scale, same tilt, same lighting direction, "
    "same depth of field, same background framing.\n"
    "IMAGE 2 is a STYLE REFERENCE only. Look at how the cob in IMAGE 2 is "
    "diseased: most of the cob is still healthy yellow/orange, the husks "
    "are just dry-tan, the field around it is still mostly alive. Only the "
    "very tip of the cob has a small cluster of black/dark sick kernels "
    "(corn smut spots) and a few scattered shrivelled brown kernels nearby. "
    "This is the AMOUNT of damage you must apply.\n"
    "\n"
    "Now produce IMAGE 1 with the SAME mild disease state shown in IMAGE 2:\n"
    " • The cob from IMAGE 1: keep ~75-80% of kernels healthy yellow-orange, "
    "shiny, plump (exactly as in IMAGE 1). Add visible disease ONLY at the "
    "top tip and upper-quarter of the cob: a small cluster of "
    "dark-purple/black smut kernels at the very top (about the size of a "
    "thumbprint), and a sparse handful of shrivelled brown-red kernels "
    "scattered in the upper portion. Lower 3/4 of the cob must remain "
    "essentially the same as IMAGE 1 (mostly healthy with maybe 2-3 darker "
    "kernels barely visible).\n"
    " • Husk leaves wrapped around the cob: keep their exact shape and "
    "position from IMAGE 1, but shift the color from vivid green to a "
    "late-season dry yellowish-tan. NOT brown crumbling — just dry. Edges "
    "may show subtle curl. Husks must STILL look intact.\n"
    " • Background corn leaves / stalks: keep the same composition as IMAGE 1 "
    "(do not change their position or focus). Color: shift slightly from "
    "vivid green to a duller olive-green / slightly yellowing — still alive, "
    "just stressed. NOT dried out.\n"
    " • Sky / far background: keep the same diffuse soft daylight as IMAGE 1. "
    "Do NOT add smog, dust, haze, or apocalyptic tones. Same calm field "
    "atmosphere.\n"
    " • Soil/foreground: same as IMAGE 1, maybe slightly drier-looking. NO "
    "cracked earth.\n"
    "\n"
    "GOAL: a viewer dragging a left/right slider over the two images "
    "should see the SAME corn with subtle visible decline — like comparing "
    "a corn after light pest pressure vs a perfectly healthy one. The "
    "two photos must look like they were shot in the SAME field on the "
    "SAME day with the SAME camera — only the cob's health differs.\n"
    "\n"
    "Output: portrait image with the EXACT same aspect ratio and pixel "
    "dimensions as IMAGE 1. Do NOT add any text, borders, or watermarks."
)


async def main() -> None:
    api_key = os.environ["EMERGENT_LLM_KEY"]
    print(f"api_key: {api_key[:18]}...")

    good = Image.open(GOOD_PATH).convert("RGB")
    print(f"good: {good.size}")
    ref = Image.open(REF_MILD).convert("RGB")
    print(f"ref:  {ref.size}")

    # Backup current "too bad" version
    backup = BAD_OUT.with_name("corn-final-bad-prev.png")
    if BAD_OUT.exists() and not backup.exists():
        backup.write_bytes(BAD_OUT.read_bytes())
        print(f"backed up old bad → {backup.name}")

    # Encode both images
    buf_good = BytesIO(); good.save(buf_good, format="PNG")
    buf_ref = BytesIO(); ref.save(buf_ref, format="PNG")
    good_b64 = base64.b64encode(buf_good.getvalue()).decode("utf-8")
    ref_b64 = base64.b64encode(buf_ref.getvalue()).decode("utf-8")

    chat = LlmChat(
        api_key=api_key,
        session_id="corn-bad-mild",
        system_message=(
            "You are a top-tier retouching artist. You preserve composition "
            "and geometry pixel-for-pixel when applying photo edits. You "
            "apply only the AMOUNT of damage requested — never more."
        ),
    )
    chat.with_model("gemini", "gemini-3-pro-image-preview").with_params(
        modalities=["image", "text"]
    )

    msg = UserMessage(
        text=EDIT_PROMPT,
        file_contents=[ImageContent(good_b64), ImageContent(ref_b64)],
    )
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
