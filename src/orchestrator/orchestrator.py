"""
Orchestrator for Kasparro Agentic FB Analyst assignment.

Flow:
1. PlannerAgent.plan(user_query) -> tasks
2. DataAgent.build_summary() -> summary
3. InsightAgent.generate_insights(summary) -> hypotheses
4. EvaluatorAgent.validate(hypotheses, summary) -> validated_hypotheses
5. CreativeAgent.generate_creatives(summary) -> creative_suggestions
6. Save outputs to reports/ and logs/

This orchestrator expects the other agent files and utils to be present.
"""

import json
import os
from datetime import datetime

from src.agents.planner_agent import PlannerAgent
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.creative_agent import CreativeAgent
from src.utils.logger import get_logger

logger = get_logger("orchestrator")


class Orchestrator:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = config_path
        # Instantiate agents
        self.planner = PlannerAgent(config_path)
        self.data_agent = DataAgent(config_path)
        self.insight_agent = InsightAgent(config_path)
        self.evaluator = EvaluatorAgent(config_path)
        self.creative = CreativeAgent(config_path)

        # load config to get paths
        import yaml
        with open(config_path, "r") as fh:
            cfg = yaml.safe_load(fh)
        self.reports_dir = cfg["paths"]["reports"]
        self.logs_dir = cfg["paths"]["logs"]

        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Local uploaded dataset path (provided by user/tooling)
        # This path can be transformed to a URL by your tooling if needed.
        self.dataset_local_path = cfg["paths"]["data"]

    def _save_json(self, obj, filename):
        path = os.path.join(self.reports_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {path}")

    def _append_log(self, entry, filename="pipeline_log.json"):
        path = os.path.join(self.logs_dir, filename)
        # append entry as a new line in NDJSON style for easy ingestion
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _save_report_md(self, text, filename="report.md"):
        path = os.path.join(self.reports_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info(f"Saved {path}")

    def run(self, user_query: str):
        run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        logger.info(f"Starting pipeline run {run_id} for query: {user_query}")

        step_events = []

        def record(step: str, status: str, detail: str | None = None):
            step_events.append({
                "step": step,
                "status": status,
                "detail": detail,
                "timestamp": datetime.utcnow().isoformat()
            })

        record("pipeline", "started", f"Run {run_id}")

        # 1) Planner
        record("planner", "started")
        try:
            plan = self.planner.plan(user_query)
            record("planner", "completed", f"{len(plan.get('tasks', []))} tasks")
        except Exception as e:
            logger.exception("Planner failed")
            plan = {"tasks": []}
            record("planner", "failed", str(e))
        self._append_log({"run_id": run_id, "step": "planner", "result": plan})

        # 2) Data Agent: build summary (cleaning handled inside)
        record("data_agent", "started")
        try:
            summary = self.data_agent.build_summary()
            record("data_agent", "completed", f"Rows {summary['dataset_info']['rows']}")
        except Exception as e:
            logger.exception("DataAgent failed")
            record("data_agent", "failed", str(e))
            raise

        self._append_log({"run_id": run_id, "step": "data_summary", "rows": summary["dataset_info"]["rows"]})

        # 3) Insight Agent
        record("insight_agent", "started")
        try:
            insights = self.insight_agent.generate_insights(summary)
            record("insight_agent", "completed", f"{len(insights.get('hypotheses', []))} insights")
        except Exception as e:
            logger.exception("InsightAgent failed")
            insights = {"hypotheses": [], "__error": str(e)}
            record("insight_agent", "failed", str(e))
        self._append_log({"run_id": run_id, "step": "insight", "insight_count": len(insights.get("hypotheses", []))})

        # 4) Evaluator Agent
        record("evaluator_agent", "started")
        try:
            validated = self.evaluator.validate(insights, summary)
            if "__error" in insights:
                validated["__error"] = insights["__error"]
            record("evaluator_agent", "completed", f"{len(validated.get('validated_hypotheses', []))} validated")
        except Exception as e:
            logger.exception("EvaluatorAgent failed")
            validated = {"validated_hypotheses": [], "__error": f"EvaluatorAgent exception: {str(e)}"}
            if "__error" in insights:
                validated["__error"] = insights["__error"]
            record("evaluator_agent", "failed", str(e))
        self._append_log({"run_id": run_id, "step": "evaluation", "validated_count": len(validated.get("validated_hypotheses", []))})

        # 5) Creative Agent
        record("creative_agent", "started")
        try:
            creatives = self.creative.generate_creatives(summary)
            record("creative_agent", "completed", f"{len(creatives.get('improvements', []))} improvements")
        except Exception as e:
            logger.exception("CreativeAgent failed")
            creatives = {"improvements": [], "__error": str(e)}
            record("creative_agent", "failed", str(e))
        self._append_log({"run_id": run_id, "step": "creative", "improvement_count": len(creatives.get("improvements", []))})

        # 6) Save structured outputs (include errors if present)
        if "__error" in insights:
            validated["__error"] = insights["__error"]
        self._save_json(validated, "insights.json")

        if "__error" in creatives:
            creatives["__error"] = creatives["__error"]
        self._save_json(creatives, "creatives.json")

        # 7) Build a simple human-readable report.md
        report_lines = []
        report_lines.append(f"# Kasparro Agentic FB Analyst Report")
        report_lines.append(f"Run ID: {run_id}")
        report_lines.append(f"Query: {user_query}")
        report_lines.append(f"Dataset (local path): {self.dataset_local_path}")
        report_lines.append("")
        report_lines.append("## Summary")
        report_lines.append(f"- Rows processed: {summary['dataset_info']['rows']}")
        report_lines.append(f"- Dates: {summary['daily_summary'][0]['date'] if summary['daily_summary'] else 'N/A'} to {summary['daily_summary'][-1]['date'] if summary['daily_summary'] else 'N/A'}")
        report_lines.append("")
        report_lines.append("## Validated Insights")
        for vh in validated.get("validated_hypotheses", []):
            report_lines.append(f"- Reason: {vh.get('reason')}")
            report_lines.append(f"  - Validated: {vh.get('validated')}")
            report_lines.append(f"  - Numeric support: {vh.get('numeric_support')}")
            report_lines.append(f"  - Final confidence: {vh.get('final_confidence')}")
        report_lines.append("")
        report_lines.append("## Creative Recommendations (sample)")
        if creatives.get("improvements"):
            for c in creatives["improvements"]:
                report_lines.append(f"- Campaign: {c.get('campaign', 'N/A')}")
                report_lines.append(f"  - Old: {c.get('old_message')}")
                report_lines.append(f"  - New Headlines: {', '.join(c.get('new_headlines', [])[:3])}")
        else:
            report_lines.append("- No creative improvements generated.")

        report_text = "\n".join(report_lines)
        self._save_report_md(report_text, filename="report.md")

        # 8) Final log entry
        self._append_log({"run_id": run_id, "step": "complete", "timestamp": datetime.utcnow().isoformat()})
        logger.info(f"Run {run_id} completed. Reports written to: {self.reports_dir} Logs: {self.logs_dir}")
        record("pipeline", "completed", f"Run {run_id}")
        return step_events
