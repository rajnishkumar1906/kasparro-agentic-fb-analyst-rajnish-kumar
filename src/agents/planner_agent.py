"""
src/agents/planner_agent.py

The Planner Agent receives the user's query (e.g., "Analyze ROAS drop")
and decomposes it into a set of structured tasks.

It uses LLMClient to generate a JSON list of steps:
[
  {"step": 1, "task": "Load and clean dataset"},
  {"step": 2, "task": "Create daily performance summary"},
  ...
]
"""

from src.utils.llm_client import MultiLLM
import yaml

class PlannerAgent:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, "r") as fh:
            self.config = yaml.safe_load(fh)

        # FIXED: MultiLLM takes NO arguments
        self.llm = MultiLLM()

    def plan(self, user_query: str) -> dict:

        system_prompt = (
            "You are the Planner Agent in a multi-agent system for Facebook Ads analysis. "
            "Your job is to break the user's query into structured, ordered steps. "
            "Always output JSON only."
        )

        user_prompt = f"""
Decompose the following query into an ordered plan with clear, atomic tasks.

User query: "{user_query}"

Return JSON:
{{
  "tasks": [
    {{"step": 1, "task": "..." }},
    {{"step": 2, "task": "..." }}
  ]
}}
"""

        result = self.llm.ask_json(system_prompt, user_prompt)

        if "tasks" not in result:
            result = {"tasks": [], "__raw": result}

        return result
