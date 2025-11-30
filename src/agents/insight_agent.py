"""
src/agents/insight_agent.py

Insight Agent:
- Receives the data summary from DataAgent
- Calls LLM to analyze trends
- Produces hypotheses explaining ROAS changes, CTR shifts, and creative/audience performance
- Returns strictly JSON
"""

import yaml
from src.utils.llm_client import MultiLLM

class InsightAgent:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # FIXED: MultiLLM takes NO arguments
        self.llm = MultiLLM()

    def generate_insights(self, summary: dict) -> dict:

        system_prompt = (
            "You are the Insight Agent for Facebook Ads performance analysis. "
            "Return ONLY JSON. No text outside JSON."
        )

        summary_text = str(summary)

        user_prompt = f"""
Analyze the following Facebook Ads summary data:

{summary_text}

Generate hypotheses for:
- ROAS change
- CTR change
- audience behavior
- creative performance
- spend fluctuations

Return this exact JSON format:
{{
  "hypotheses": [
    {{
      "reason": "...",
      "evidence": "...",
      "metric": "...",
      "confidence": 0.0
    }}
  ]
}}
"""

        try:
            response = self.llm.ask_json(system_prompt, user_prompt)

            if "hypotheses" not in response:
                # Check if we got a raw text response indicating failure
                if isinstance(response, dict) and "__raw_text" in response:
                    raw_text = response.get("__raw_text", "")
                    if "Model failed" in raw_text or len(raw_text) < 50:
                        return {"hypotheses": [], "__error": f"LLM failed to generate valid response: {raw_text[:200]}"}
                return {"hypotheses": [], "__raw": response, "__error": "Response missing 'hypotheses' key"}

            # Validate that we actually got hypotheses
            if not response.get("hypotheses") or len(response.get("hypotheses", [])) == 0:
                return {"hypotheses": [], "__error": "LLM returned empty hypotheses list"}

            return response
        except Exception as e:
            import traceback
            error_msg = f"InsightAgent exception: {str(e)}"
            print(f"[INSIGHT_AGENT] {error_msg}")
            print(traceback.format_exc())
            return {"hypotheses": [], "__error": error_msg}
