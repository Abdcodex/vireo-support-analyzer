# Submission Form — Vireo Audio Support Tickets

## Business goal

Use the ₹4 lakh Q3 training budget on a reviewed set of Tier 1 agents rather than blindly allocating it from a raw ranking. A concrete operational target is to reduce the H1 2026 replacement rate for the four Chat Frontline agents in the raw bottom-ten from 39.4% toward 30% over six months. At their observed replacement-cost mix, this corresponds to approximately ₹1.11 lakh of modeled replacement-cost opportunity over six months. This is a scenario, not a causal forecast.

## What does the tool do?

It calculates CSAT, top-box CSAT, response rate, handle time, SLA breaches, replacement rate/cost, monthly trends, agent-level metrics, the requested raw bottom ten, and a queue-aware review view. It also includes a local AI/ML text classifier and qualitative ticket-insight fields.

## Sample size / checks

- 11,750 tickets.
- 5,196 CSAT responses.
- 44.2% CSAT response rate.
- 44 agents.
- 2,309 raw negative handle times were detected in legacy tickets and corrected using the documented UTC-to-IST normalization.
- 0 negative handle times remain after normalization.
- 0 duplicate ticket IDs.
- Agent joins use agent_id.

## AI validation

- Model: local TF-IDF + LogisticRegression.
- Validation sample: 300 tickets.
- Holdout accuracy against existing intake category: 76.3%.
- Error rate: 23.7%.
- Failure type: confusion among semantically similar categories.
- Important limitation: intake category is a proxy label, not human-reviewed gold truth. Dissatisfaction-driver, sentiment and apparent-resolution outputs still require human review.
- API/model-call cost: ₹0 for the working implementation.

## Did you change, narrow, or push back on the client ask?

Yes, narrowly.

The requested raw bottom-ten view is retained so the client ask is directly answered. However, the submission does not treat the raw ranking as the sole basis for training allocation. Tier 2 is excluded from the Tier 1 comparison because the policy says Tier 2 should not be compared with Tier 1 on volume metrics. Queue mix is also treated as a confounder because the Support Operations Manager explicitly warns that hardware triage/warranty queues receive angrier customers by design.

The four Chat Frontline agents in the raw bottom ten are therefore surfaced as a focused review set, not automatically declared to be the agents who caused poor CSAT.

## Key findings

H1 2026 vs H1 2025:

- Top-box CSAT: 51.8% → 41.4% (-10.4pp).
- Median handle time: 26 → 31 minutes (+5 minutes).
- Replacement rate: 9.5% → 22.3% (+12.7pp).
- H1 2026 replacement planning cost: ₹22.14 lakh.

## Limitations

- Observational data does not establish causality.
- Queue mix and issue severity confound agent comparisons.
- CSAT has non-response bias.
- Legacy timestamps require UTC-to-IST normalization.
- Mean handle time is highly skewed by operational queues; median is the primary comparison metric.
- AI validation is proxy-label validation, not human gold-label validation.
- Replacement-cost scenarios are not guaranteed savings.

## Deliberate omissions

- Predictive agent-performance model.
- Causal model.
- Customer profiling.
- Lot-code analysis.
- Production deployment.
- Paid per-ticket LLM calls.

## Extra analysis

- Monthly CSAT/handle-time/replacement trends.
- Replacement-cost analysis using the policy-defined unit-cost + ₹340 formula.
- Queue-aware training-review view.
- AI-assisted ticket classification and qualitative coaching signals.

## AI use / discarded approaches

The working tool uses a local TF-IDF + LogisticRegression classifier so the full dashboard runs without an external API. A paid LLM-per-ticket design was not used because it would add recurring cost without being necessary for the deterministic dashboard metrics. The optional LLM prompt specification is included for future extension.
