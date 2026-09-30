# Vireo Audio — Support Ticket Analytics

A reproducible Python/Streamlit analysis for **Vireo Audio — Support Tickets (Set B), Task 1 V4**.

## What this tool answers

1. What changed in customer support performance?
2. What does the requested bottom-ten agent view look like?
3. Why should that raw ranking not be treated as the sole training allocation rule?
4. What operational signals accompany CSAT (handle time, SLA breaches, replacements/cost)?
5. What qualitative issue/dissatisfaction themes can a lightweight local AI/ML classifier surface?

## Data

The `data/raw/` directory contains the supplied CSV exports plus the supplied policy/email/support-pack text/PDF materials. The analysis uses the CSVs as the computational source of truth and the policy/email as the methodology source of truth.

## Requirements

- Python 3.11+ recommended
- pip

## Install

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run analysis

```bash
python run_analysis.py
```

This creates:

- `outputs/agent_metrics.csv`
- `outputs/monthly_metrics.csv`
- `outputs/period_metrics.csv`
- `outputs/raw_bottom_ten.csv`
- `outputs/training_candidates.csv`
- `outputs/training_focus.csv`
- `outputs/classified_tickets.csv`
- `outputs/validation_results.csv`

## Run dashboard

```bash
streamlit run app.py
```

The dashboard contains:

- Executive Overview
- Agent Dashboard
- Raw Bottom Ten
- Training Priorities
- AI Insights
- Methodology & Limitations

## Run tests

```bash
pytest
```

## Methodology

### CSAT

CSAT is the supplied 1–5 survey score. Blank scores are no responses and are excluded from the CSAT denominator. **Top-box CSAT = scores 4 or 5.**

### Handle time

Handle time follows the supplied policy: **first human response to resolution**.

The support policy states that helpdesk display/export timestamps are IST, while reconstructed legacy resolution timestamps come from a UTC event log. The raw data contains 2,309 negative handle times before normalization. For legacy rows with a resolution timestamp, the implementation adds 5h30 to the reconstructed resolution timestamp. After normalization, there are zero negative handle times.

Median handle time is the primary comparison because operational queues contain long elapsed durations that heavily skew the mean.

### Tier handling

Tier 2 is retained in the dashboard but excluded from the Tier 1 raw training comparison. The supplied policy explicitly says Tier 2 agents should not be compared with Tier 1 on volume metrics and that Tier 2 work is measured differently.

### Agent joins

Agent IDs are used as the stable join key, not names. This follows the supplied administrator note because two agents share the display name Kavya Pandey.

### Replacement cost

Replacement planning cost = product unit cost + ₹340 reverse pickup/forward shipping, per the supplied policy. The finance email's rough ₹2,500 figure is not used for planning because the email itself says the policy definition is unit cost + ₹340.

### Queue mix

The supplied Support Operations Manager email warns that the hardware triage/warranty queues receive angrier customers by design. Therefore the raw CSAT ranking is treated as a descriptive screening view, not a causal measure of agent quality.

## AI/ML component

The working implementation deliberately avoids a paid LLM call per ticket. It uses a local **TF-IDF + LogisticRegression** text classifier to predict the existing intake category from customer messages and agent notes. It also produces lightweight heuristic fields for sentiment, dissatisfaction driver, and apparent resolution.

The model was evaluated on a 300-ticket holdout sample against the existing intake category as a **proxy label**:

- validation sample: 300
- holdout accuracy: 76.3%
- holdout error rate: 23.7%
- mean test confidence: 43.0%

This is not human gold-label validation. In particular, the dissatisfaction-driver and apparent-resolution fields require human review before they are treated as authoritative.

The optional LLM prompt specification is stored in `prompts/ticket_classifier.txt`, but no per-ticket paid LLM calls are required to run the submission. Model/API cost for the working implementation is ₹0.

## Business goal

Use the ₹4 lakh Q3 training budget on a reviewed set of Tier 1 agents rather than blindly allocating it from a raw ranking. A concrete operational target is to reduce the H1 2026 replacement rate for the four Chat Frontline agents in the raw bottom-ten from **39.4% toward 30%** over a six-month follow-up period. At the observed replacement-cost mix for those agents, that target corresponds to a **scenario opportunity of approximately ₹1.11 lakh over six months** (about ₹55.7k per quarter). This is a scenario, not a causal forecast or guaranteed saving.

## Limitations

- Observational data cannot establish that an agent caused a customer's CSAT score.
- Queue mix and customer issue severity can confound agent comparisons.
- CSAT is response-biased because only about 44% of tickets in this export have a survey response.
- Legacy timestamp normalization is based on the supplied policy's UTC/IST description.
- Mean handle time is highly skewed by operational queues; median is used for frontline comparison.
- The AI classifier's validation target is an existing intake category, not a human-reviewed truth set.
- AI-derived dissatisfaction drivers and resolution labels should be reviewed before operational use.
- The replacement-cost scenario is not a causal ROI estimate.

## Deliberate omissions

- No predictive agent-performance model.
- No causal model claiming that training will create a specific CSAT or cost lift.
- No customer demographic/profile scoring.
- No lot-code analysis because the supplied email says it was historical Finance context and is not necessary for the dashboard question.
- No production deployment or external database.
- No paid per-ticket LLM pipeline because the supplied Finance request explicitly asks to keep the tool cheap to run.
