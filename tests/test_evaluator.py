"""
Basic unit tests for EvaluatorAgent.

These tests ensure:
- evaluator loads without error
- evaluator returns expected fields
- hypotheses are validated numerically
"""

import pytest
from src.agents.evaluator_agent import EvaluatorAgent


def test_evaluator_basic_validation():
    evaluator = EvaluatorAgent("config/config.yaml")

    # Fake summary similar to DataAgent output
    summary = {
        "daily_summary": [
            {"date": "2025-01-01", "ctr": 0.02, "roas": 3.0},
            {"date": "2025-01-02", "ctr": 0.01, "roas": 2.0},   # CTR + ROAS dropped
        ],
        "creative_summary": [
            {"creative_type": "Video", "ctr": 0.03},
            {"creative_type": "Image", "ctr": 0.01}
        ],
        "audience_summary": [
            {"audience_type": "Broad", "ctr": 0.02},
            {"audience_type": "Retarget", "ctr": 0.03}
        ],
    }

    # Fake hypotheses from InsightAgent
    hypotheses = {
        "hypotheses": [
            {
                "reason": "CTR dropped due to creative fatigue",
                "evidence": "Daily CTR decreased",
                "metric": "ctr",
                "confidence": 0.6
            }
        ]
    }

    result = evaluator.validate(hypotheses, summary)

    # Structural checks
    assert "validated_hypotheses" in result
    assert len(result["validated_hypotheses"]) == 1

    h = result["validated_hypotheses"][0]

    # Field presence
    assert "validated" in h
    assert "numeric_support" in h
    assert "final_confidence" in h

    # Numeric check: ctr dropped from 0.02 to 0.01, so validated=True
    assert h["validated"] is True
    assert h["numeric_support"] == pytest.approx(-0.01)