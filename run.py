"""
run.py
Main entry point for Kasparro Agentic Facebook Analyst Pipeline.

Usage:
    python run.py "Analyze ROAS drop"
"""

import sys
from src.orchestrator.orchestrator import Orchestrator


def main():
    if len(sys.argv) < 2:
        print("❌ Error: You must provide a query.")
        print("Example: python run.py 'Analyze ROAS drop'")
        return

    user_query = sys.argv[1]
    print(f"\n🚀 Running Kasparro Agentic FB Analyst\nQuery: {user_query}\n")

    orchestrator = Orchestrator("config/config.yaml")
    orchestrator.run(user_query)

    print("\n✅ Pipeline completed.")
    print("📁 Check 'reports/' for:")
    print("   - insights.json")
    print("   - creatives.json")
    print("   - report.md")
    print("\n📁 Check 'logs/' for pipeline logs.\n")


if __name__ == "__main__":
    main()
