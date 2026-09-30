# 3-Minute Demo Script

## 0:00–0:25 — README / problem

"This is a reproducible Streamlit tool for Vireo Audio's support-ticket assessment. The client asked for CSAT, handle time and a bottom-ten view. I kept that requested view, but I also tested whether the ranking was fair enough to drive training allocation."

## 0:25–0:55 — Data-quality check

"One important issue was legacy timestamps. The source policy says the helpdesk is IST but reconstructed legacy resolution timestamps are UTC. The raw data produced 2,309 negative handle times. I normalize those legacy resolutions by 5 hours 30 minutes, and the resulting dataset has zero negative handle times."

## 0:55–1:25 — Executive dashboard

Show the overview.

"The key period change is H1 2025 to H1 2026: top-box CSAT fell 10.4 percentage points, median handle time increased 5 minutes, and replacement rate increased 12.7 percentage points."

## 1:25–1:55 — Raw bottom ten

Show the raw ranking.

"This directly answers the client request. But I don't treat it as a causal quality ranking. Tier 2 is excluded from the Tier 1 comparison, and the operations email specifically warns that queue mix can create angry-customer effects."

## 1:55–2:20 — Focused review set

Show the four Chat Frontline agents from the raw bottom ten.

"These four are surfaced for manager review because they share the Chat Frontline benchmark and are less directly affected by the documented hardware/warranty queue warning. This is a review set, not an automatic retraining verdict."

## 2:20–2:45 — AI

Show AI Insights.

"The AI component is deliberately cheap: local TF-IDF plus LogisticRegression, not a paid LLM call per ticket. On a 300-ticket holdout against the existing intake category, accuracy is 76.3%. That's proxy validation, not human gold-label validation, so I flag that limitation."

## 2:45–3:00 — Close

"The business target is to improve CSAT for the focused review set while reducing their replacement rate from 39.4% toward 30% over six months. At observed replacement cost, that's about ₹1.11 lakh of modeled opportunity. The number is explicitly a scenario, not a causal forecast."
