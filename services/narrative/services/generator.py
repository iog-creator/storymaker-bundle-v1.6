# narrative/services/generator.py
from typing import Dict, Any, List
import json

# Use the scribe Groq generator that loads prompts from docs/prompts/scribe_prompts.json
from services.narrative.scribe.hf_client import generate as groq_generate

# UI names → mode ids are handled in the web client; here we map ids to human-readable names
STRUCTURE_NAMES: Dict[str, str] = {
    "hero_journey": "Hero's Journey",
    "harmon_8": "Harmon 8",
    "kishotenketsu": "Kishotenketsu",
}

def generate_outline(world_id: str, premise: str, mode: str) -> Dict[str, Any]:
    """Generate a full outline in one Groq call using the JSON-returning outline prompt.

    Returns shape: { status, data: { world_id, mode, beats } }
    where beats is what the prompt emits (objective/turn/value_shift/promises...).
    """
    try:
        structure_name = STRUCTURE_NAMES.get(mode, STRUCTURE_NAMES["hero_journey"])

        # Call Groq with the outline task; the prompt specifies a JSON object in the output
        out = groq_generate(
            "outline",
            {
                "premise": premise,
                "structure": structure_name,
                "axis": "control → freedom",
                "canon": "",
                "trope_bans": [
                    "chosen one",
                    "ancient prophecy",
                    "dark lord",
                    "it was all a dream",
                    "mysterious stranger",
                    "forbidden forest",
                    "destined to",
                ],
            },
        )

        # The model draft should be JSON per the prompt contract
        try:
            draft_text = out.get("draft", "")
            if isinstance(draft_text, dict):
                payload = draft_text
            else:
                text = str(draft_text)
                try:
                    payload = json.loads(text)
                except Exception:
                    # Be tolerant to prose-wrapped JSON: extract first {...} block
                    start = text.find("{")
                    end = text.rfind("}")
                    if start != -1 and end != -1 and end > start:
                        payload = json.loads(text[start : end + 1])
                    else:
                        raise
        except Exception as parse_error:
            return {
                "status": "error",
                "error": "outline_parse_failed",
                "meta": {"cause": str(parse_error), "draft_preview": str(out.get("draft", ""))[:400]},
            }

        beats: List[Dict[str, Any]] = payload.get("beats", [])

        return {
            "status": "ok",
            "data": {"world_id": world_id, "mode": mode, "beats": beats},
        }
    except Exception as e:
        return {"status": "error", "error": "groq_unavailable", "meta": {"cause": str(e), "provider": "groq"}}
