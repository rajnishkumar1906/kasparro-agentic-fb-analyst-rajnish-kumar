# 🧠 Kasparro Agentic FB Analyst — Rajnish Kumar

An Agentic AI system that autonomously analyzes Facebook Ads performance, diagnoses ROAS fluctuations, validates hypotheses using quantitative signals, and generates new creative recommendations grounded in real ad messaging.

Built for the **Kasparro Applied AI Engineer Assignment**.

---

## 🚀 Project Highlights

* Multi-agent architecture (Planner → Data → Insight → Evaluator → Creative)
* Structured prompting with JSON/Markdown enforced outputs
* Quantitative validation layer using CTR/ROAS/audience metrics
* Full agentic reasoning loop
* Data-driven creative generation for low-CTR ads
* CLI interface:

  ```
  python run.py "Analyze ROAS drop"
  ```

---

## 📁 Repository Structure

```
kasparro-agentic-fb-analyst-rajnish-kumar/
│
├── README.md
├── requirements.txt
├── run.py
├── queries.txt
│
├── config/
│   └── config.yaml
│
├── data/
│   ├── synthetic_fb_ads_undergarments.csv
│   └── README.md
│
├── logs/
│   └── pipeline_log.json
│
├── prompts/
│   ├── planner_prompt.md
│   ├── insight_prompt.md
│   ├── evaluator_prompt.md
│   └── creative_prompt.md
│
├── reports/
│   ├── report.md
│   ├── insights.json
│   └── creatives.json
│
├── src/
│   ├── agents/
│   │   ├── planner_agent.py
│   │   ├── data_agent.py
│   │   ├── insight_agent.py
│   │   ├── evaluator_agent.py
│   │   └── creative_agent.py
│   │
│   ├── orchestrator/
│   │   └── orchestrator.py
│   │
│   └── utils/
│       ├── cleaner.py
│       ├── helpers.py
│       ├── logger.py
│       └── llm_client.py
│
└── tests/
    └── test_evaluator.py
```

---

## 🧩 Agent Architecture

```
Planner Agent
    ↓
Data Agent
    ↓
Insight Agent
    ↓
Evaluator Agent
    ↓
Creative Agent
```

---

## ⚙️ Installation

### 1. Clone repository

```bash
git clone https://github.com/rajnishkumar1906/kasparro-agentic-fb-analyst-rajnish-kumar.git
cd kasparro-agentic-fb-analyst-rajnish-kumar
```

### 2. Create environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage (CLI)

Run any analysis:

```bash
python run.py "Analyze ROAS drop"
```

Other examples:

```bash
python run.py "Why did ROAS decline?"
python run.py "Find audience fatigue signals"
python run.py "Generate new creative ideas"
```

---

## 📤 Generated Outputs

All generated files are stored in `/reports/`:

| File           | Description                               |
| -------------- | ----------------------------------------- |
| insights.json  | Validated hypotheses with confidence      |
| creatives.json | Headlines, captions, CTAs for low-CTR ads |
| report.md      | Final report used by marketers            |

Logs are stored in:

```
/logs/pipeline_log.json
```

---

## 🔍 Sample Output

### insights.json

```json
{
  "reason": "Retargeting audiences outperform broad",
  "validated": true,
  "numeric_support": 0.0128,
  "final_confidence": 1.0
}
```

### creatives.json

```json
{
  "campaign": "Men Comfortmax Launch",
  "oldmessage": "Cooling mesh panels...",
  "newheadlines": ["Workout Boxers That Keep You Cool"],
  "newcaptions": ["Stay cool during intense sessions"],
  "newctas": ["Shop Now"]
}
```

---

## 🧪 Testing

Run evaluator tests:

```bash
pytest tests/test_evaluator.py -q
```

---

## 🔖 Reproducibility & Git Hygiene

* Pinned package versions
* Deterministic outputs via config flags
* includes: `report.md`, `insights.json`, `creatives.json`, logs
* Multiple commits + v1.0 release tag
* Clean folder structure following Kasparro requirements

---

## 👤 Author

**Rajnish Kumar**
Applied AI Engineer — Kasparro Assignment

---

