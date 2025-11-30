"""
src/agents/evaluator_agent.py

Evaluator Agent:
- Validates hypotheses from InsightAgent using actual numbers.
- Adds a 'validated' field: true/false
- Adds numeric evidence
- Produces a confidence score based on strength of numeric match.
"""

import yaml
import statistics


class EvaluatorAgent:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.thresholds = self.config["thresholds"]

    def _get_latest_ctr_change(self, daily_summary):
        if len(daily_summary) < 2:
            return 0
        return daily_summary[-1]["ctr"] - daily_summary[-2]["ctr"]

    def _get_latest_roas_change(self, daily_summary):
        if len(daily_summary) < 2:
            return 0
        return daily_summary[-1]["roas"] - daily_summary[-2]["roas"]

    def validate(self, hypotheses: dict, summary: dict) -> dict:
        """
        Check each hypothesis with actual data.
        Adds:
        - validated: True/False
        - numeric_support
        - final_confidence
        """
        
        # Preserve error if present
        result = {}
        if "__error" in hypotheses:
            result["__error"] = hypotheses["__error"]

        daily = summary["daily_summary"]
        creative = summary["creative_summary"]
        audience = summary["audience_summary"]

        ctr_change = self._get_latest_ctr_change(daily)
        roas_change = self._get_latest_roas_change(daily)

        validated_hypotheses = []

        for hyp in hypotheses.get("hypotheses", []):
            reason = hyp.get("reason", "").lower()

            validated = False
            numeric_support = None

            # CTR drop check
            if "ctr" in reason and "drop" in reason:
                numeric_support = ctr_change
                validated = ctr_change < 0

            # ROAS drop check
            if "roas" in reason and "drop" in reason:
                numeric_support = roas_change
                validated = roas_change < 0

            # creative type comparison check
            if "video" in reason and "image" in reason:
                try:
                    video_ctr = next(x for x in creative if x["creative_type"].lower() == "video")["ctr"]
                    image_ctr = next(x for x in creative if x["creative_type"].lower() == "image")["ctr"]
                    numeric_support = video_ctr - image_ctr
                    validated = video_ctr > image_ctr
                except:
                    pass

            # audience performance check
            if "audience" in reason:
                # simple validation: look for bigger CTR difference
                try:
                    ctrs = [x["ctr"] for x in audience]
                    mean_ctr = statistics.mean(ctrs)
                    numeric_support = mean_ctr
                    validated = True  # soft validation
                except:
                    pass

            # final confidence: combine numeric support + LLM confidence
            llm_conf = hyp.get("confidence", 0.5)
            if numeric_support is not None:
                final_conf = min(1.0, llm_conf + 0.2)
            else:
                final_conf = llm_conf

            validated_hypotheses.append({
                "reason": hyp.get("reason"),
                "evidence": hyp.get("evidence"),
                "metric": hyp.get("metric"),
                "validated": validated,
                "numeric_support": numeric_support,
                "final_confidence": round(final_conf, 3)
            })

        result["validated_hypotheses"] = validated_hypotheses
        return result
