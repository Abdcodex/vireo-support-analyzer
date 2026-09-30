# Vireo Audio Support Dashboard — Executive Memo

**To:** Priya Raman, Head of Customer Experience  
**Subject:** CSAT, handle time and training review — Support Tickets Set B

## Executive summary

The export contains 11,750 tickets from January 2025 through June 2026. There are 5,196 CSAT responses (44.2%). Using top-box CSAT (scores 4–5), the overall top-box rate is 45.8%.

Comparing H1 2026 with H1 2025:

- Top-box CSAT fell from **51.8% to 41.4% (-10.4 percentage points)**.
- Median handle time increased from **26 to 31 minutes (+5 minutes)**.
- Replacement rate increased from **9.5% to 22.3% (+12.7 percentage points)**.
- H1 2026 replacement planning cost was **₹22.14 lakh**, using the policy definition of product unit cost + ₹340 logistics.

The requested raw bottom-ten view is included. I would not use that ranking alone to allocate the ₹4 lakh training budget because the supplied Operations Manager email explicitly warns that queue mix can confound agent comparisons, and the policy says Tier 2 should not be compared with Tier 1 on volume metrics.

## Data-quality check

The raw data produced 2,309 negative handle times. The supplied policy explains why: reconstructed legacy resolution timestamps come from a UTC event log while helpdesk timestamps are displayed/exported in IST. The analysis adds 5h30 to legacy reconstructed resolution timestamps. After normalization, negative handle times fall to zero.

Agent joins use `agent_id`, not display name, because the supplied administrator email notes that two agents share the name Kavya Pandey.

## Requested bottom-ten view

The raw Tier 1 bottom-ten ranking is:

| Agent | Team | CSAT responses | Top-box CSAT | Median handle time |
|---|---|---:|---:|---:|
| Siddharth Kapoor (A3004) | Chat Frontline | 129 | 31.8% | 26 min |
| Vivaan Pandey (A3028) | Logistics | 154 | 31.8% | 1,463 min |
| Kavya Pandey (A3029) | Logistics | 159 | 33.3% | 1,466 min |
| Divya Tiwari (A3036) | Returns Desk | 106 | 35.8% | 1,466 min |
| Geeta Iyer (A3030) | Logistics | 150 | 37.3% | 1,466 min |
| Zaid Khanna (A3005) | Chat Frontline | 118 | 38.1% | 25 min |
| Varun Reddy (A3038) | Returns Desk | 121 | 38.8% | 1,467 min |
| Siddharth Trivedi (A3007) | Chat Frontline | 120 | 40.0% | 27 min |
| Mohammed Desai (A3037) | Returns Desk | 243 | 40.7% | 1,473 min |
| Kavya Pandey (A3006) | Chat Frontline | 142 | 42.3% | 27 min |

The table is descriptive. It should not be read as proof that these agents are individually responsible for the observed CSAT results.

## Focused training-review set

The four Chat Frontline agents appearing in the raw bottom-ten are surfaced as a focused review set because their relevant team benchmark is available and the Operations Manager's hardware/warranty queue warning is less directly applicable to their queue.

Combined across the full period, these four agents have 509 CSAT responses and 38.1% top-box CSAT versus 51.2% for Chat Frontline. In H1 2026 specifically, they handled 655 tickets, had 31.1% top-box CSAT among 289 responses, and had a 39.4% replacement rate.

This is a **review set**, not an automatic retraining verdict. Manager review should consider ticket examples and queue context before spending training budget.

## Business goal and money

A practical follow-up target is to reduce the H1 2026 replacement rate for this four-agent review set from **39.4% toward 30%** over six months while improving their CSAT toward the relevant team benchmark.

At their observed H1 2026 replacement-cost mix, moving from 39.4% to 30% would correspond to approximately **61 fewer replacements and ₹1.11 lakh of modeled replacement-cost opportunity over six months**. This is a scenario calculation, not a causal forecast or guaranteed saving.

The ₹4 lakh training budget should therefore be treated as a budget constraint, not as proof that the modeled opportunity will exceed training spend.

## Root-cause / AI-assisted view

The working tool uses a local TF-IDF + LogisticRegression classifier to predict the existing intake category from ticket text. On a 300-ticket holdout sample it achieved 76.3% accuracy against that existing category label, with a 23.7% error rate. The common failure mode is confusion among semantically similar categories.

The tool also surfaces heuristic dissatisfaction drivers, sentiment, and apparent resolution. These fields are explicitly marked as requiring human review; they are not treated as ground truth.

## Limitations

1. CSAT is response-biased; blanks are excluded rather than treated as dissatisfaction.
2. Agent comparisons are observational and confounded by queue mix and issue severity.
3. Tier 2 is not mixed into the Tier 1 volume ranking.
4. Legacy timestamps require the documented UTC-to-IST normalization.
5. Operational queues have multi-day elapsed handle times, making the median more useful than the mean for frontline comparisons.
6. AI validation uses intake categories as proxy labels, not a human gold-standard annotation set.
7. Replacement-cost opportunity is a scenario, not an ROI guarantee.

## Deliberate omissions

The submission does not build predictive agent scoring, causal modeling, customer profiling, lot-code analysis, production deployment, or paid per-ticket LLM calls. These would add scope or unsupported certainty without being necessary to answer the stated dashboard question.

## Next steps

1. Review the raw bottom-ten tickets and the four-agent focused set with Support Operations.
2. Sample actual conversations from the flagged agents before assigning training.
3. Use the dashboard monthly to monitor CSAT and replacement rate together.
4. Human-review a labeled sample of AI-derived dissatisfaction drivers before using them for formal coaching decisions.
