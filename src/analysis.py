from pathlib import Path
import pandas as pd
from .data_loader import load_data
from .metrics import prepare_tickets, summary_metrics, period_metrics, monthly_metrics, agent_metrics, raw_bottom_ten, training_candidates
from .ai_classifier import classify_dataset

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


def run():
    tickets, agents, orders, customers, products = load_data()
    t = prepare_tickets(tickets, products)
    am = agent_metrics(t, agents)
    monthly = monthly_metrics(t)
    periods = period_metrics(t)
    bottom = raw_bottom_ten(am)
    candidates = training_candidates(am)
    focus = bottom[bottom["team"].eq("Chat Frontline")].copy()
    focus["focus_reason"] = "Appears in requested raw bottom-ten and is in Chat Frontline; team-relative gap is not explained by the Tier 2/hardware-queue warning. Requires manager review, not automatic retraining."

    am.to_csv(OUT / "agent_metrics.csv", index=False)
    monthly.to_csv(OUT / "monthly_metrics.csv", index=False)
    periods.to_csv(OUT / "period_metrics.csv", index=False)
    bottom.to_csv(OUT / "raw_bottom_ten.csv", index=False)
    candidates.to_csv(OUT / "training_candidates.csv", index=False)
    focus.to_csv(OUT / "training_focus.csv", index=False)

    # Lightweight local AI/ML classifier. It uses only ticket text and the intake category as a proxy label.
    classified, validation = classify_dataset(t, sample_size=min(1200, len(t)))
    classified.to_csv(OUT / "classified_tickets.csv", index=False)
    validation.to_csv(OUT / "validation_results.csv", index=False)
    return t, am, monthly, periods, bottom, candidates, classified, validation

if __name__ == "__main__":
    run()
