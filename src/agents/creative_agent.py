import yaml
from src.utils.llm_client import MultiLLM


class CreativeAgent:
    def __init__(self, config_path="config/config.yaml"):
        # Load config
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.ctr_threshold = self.config["thresholds"]["low_ctr"]

        self.llm = MultiLLM()

    def generate_creatives(self, summary: dict) -> dict:
        """
        Identify creatives with low CTR and generate improvements.
        """

        # Use creative_summary (already aggregated)
        items = summary["creative_summary"]

        # Filter items below threshold
        low_ctr_items = [
            {
                "campaign": x.get("campaign_name"),
                "old_message": x.get("creative_message"),
                "ctr": x.get("ctr"),
                "creative_type": x.get("creative_type")
            }
            for x in items
            if x.get("ctr") is not None and x.get("ctr") < self.ctr_threshold
        ]

        # Remove items missing creative message
        low_ctr_items = [x for x in low_ctr_items if x["old_message"]]

        # Limit to avoid LLM overload
        low_ctr_items = low_ctr_items[:5]

        if not low_ctr_items:
            return {"improvements": [], "note": "No low-CTR creatives found."}

        # LLM prompt
        system_prompt = (
            "You are a Facebook Ads Creative Agent. "
            "Your job is to improve low-CTR ads. "
            "Return ONLY JSON. No notes, no markup."
        )

        user_prompt = f"""
You are given a list of low-CTR creatives:

{low_ctr_items}

For each creative:
- Use the old_message as the base
- Maintain the product tone
- Generate:
    - 3 short headlines
    - 3 captions
    - 2–3 strong CTAs

Return STRICT JSON:

{{
  "improvements": [
    {{
      "campaign": "...",
      "old_message": "...",
      "new_headlines": ["...", "...", "..."],
      "new_captions": ["...", "...", "..."],
      "new_ctas": ["...", "..."]
    }}
  ]
}}
"""

        try:
            response = self.llm.ask_json(system_prompt, user_prompt)

            # Fallback safety
            if "improvements" not in response:
                # Check if we got a raw text response indicating failure
                if isinstance(response, dict) and "__raw_text" in response:
                    raw_text = response.get("__raw_text", "")
                    if "Model failed" in raw_text or len(raw_text) < 50:
                        return {"improvements": [], "__error": f"LLM failed to generate valid response: {raw_text[:200]}"}
                return {"improvements": [], "__raw": response, "__error": "Response missing 'improvements' key"}

            # Validate that we actually got improvements
            if not response.get("improvements") or len(response.get("improvements", [])) == 0:
                return {"improvements": [], "__error": "LLM returned empty improvements list"}

            return response
        except Exception as e:
            import traceback
            error_msg = f"CreativeAgent exception: {str(e)}"
            print(f"[CREATIVE_AGENT] {error_msg}")
            print(traceback.format_exc())
            return {"improvements": [], "__error": error_msg}
