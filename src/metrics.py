import numpy as np
import pandas as pd

CHANNEL_SLA_MIN = {"chat": 15, "voice": 120, "social": 240, "email": 480}
CONTACT_COST_INR = {"chat": 210, "email": 260, "voice": 520, "social": 240}
REPLACEMENT_LOGISTICS_INR = 340


def prepare_tickets(tickets: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    t = tickets.copy()
    for c in ["created_at", "first_response_at", "resolved_at"]:
        t[c] = pd.to_datetime(t[c], errors="coerce")
    t["csat_score"] = pd.to_numeric(t["csat_score"], errors="coerce")
    t["refund_amount_inr"] = pd.to_numeric(t["refund_amount_inr"], errors="coerce")
    t["transfers"] = pd.to_numeric(t["transfers"], errors="coerce").fillna(0)

    # Source pack/policy: helpdesk displays IST; legacy reconstructed resolution timestamps are UTC.
    t["resolved_at_normalized"] = t["resolved_at"]
    legacy = t["source_system"].eq("legacy_fd") & t["resolved_at"].notna()
    t.loc[legacy, "resolved_at_normalized"] = t.loc[legacy, "resolved_at"] + pd.Timedelta(hours=5, minutes=30)
    t["legacy_resolution_normalized"] = legacy

    t["first_response_minutes"] = (t["first_response_at"] - t["created_at"]).dt.total_seconds() / 60
    t["handle_time_minutes"] = (
        t["resolved_at_normalized"] - t["first_response_at"]
    ).dt.total_seconds() / 60
    t["sla_target_minutes"] = t["channel"].map(CHANNEL_SLA_MIN)
    t["sla_breach"] = (
        t["first_response_minutes"].notna()
        & t["sla_target_minutes"].notna()
        & (t["first_response_minutes"] > t["sla_target_minutes"])
    )
    t["csat_response"] = t["csat_score"].notna()
    t["top_box"] = t["csat_score"].isin([4, 5])
    t["attendance"] = t["status"].isin(["resolved", "closed"])
    t["replacement_issued_bool"] = t["replacement_issued"].eq("Y")
    t["contact_cost_inr"] = t["channel"].map(CONTACT_COST_INR)

    p = products[["sku", "unit_cost_inr"]].copy()
    p["unit_cost_inr"] = pd.to_numeric(p["unit_cost_inr"], errors="coerce")
    t = t.merge(p, left_on="product_sku", right_on="sku", how="left", suffixes=("", "_product"))
    t["replacement_cost_inr"] = np.where(
        t["replacement_issued_bool"], t["unit_cost_inr"] + REPLACEMENT_LOGISTICS_INR, 0.0
    )
    t["month"] = t["created_at"].dt.to_period("M").astype(str)
    t["half"] = np.where(t["created_at"].dt.month.le(6), "H1", "H2")
    t["year_half"] = t["created_at"].dt.year.astype(str) + " " + t["half"]
    return t


def summary_metrics(t: pd.DataFrame) -> dict:
    cs = t[t["csat_response"]]
    return {
        "tickets": int(len(t)),
        "csat_responses": int(len(cs)),
        "csat_response_rate_pct": float(len(cs) / len(t) * 100) if len(t) else np.nan,
        "mean_csat": float(cs["csat_score"].mean()) if len(cs) else np.nan,
        "top_box_csat_pct": float(cs["top_box"].mean() * 100) if len(cs) else np.nan,
        "median_handle_time_min": float(t["handle_time_minutes"].dropna().median()) if t["handle_time_minutes"].notna().any() else np.nan,
        "mean_handle_time_min": float(t["handle_time_minutes"].dropna().mean()) if t["handle_time_minutes"].notna().any() else np.nan,
        "sla_breach_rate_pct": float(t["sla_breach"].mean() * 100) if len(t) else np.nan,
        "replacement_count": int(t["replacement_issued_bool"].sum()),
        "replacement_rate_pct": float(t["replacement_issued_bool"].mean() * 100) if len(t) else np.nan,
        "replacement_cost_inr": float(t["replacement_cost_inr"].sum()),
    }


def period_metrics(t: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for period, g in t.groupby("year_half", sort=True):
        s = summary_metrics(g)
        s["period"] = period
        rows.append(s)
    return pd.DataFrame(rows)[["period"] + [c for c in rows[0] if c != "period"]] if rows else pd.DataFrame()


def monthly_metrics(t: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for month, g in t.groupby("month", sort=True):
        s = summary_metrics(g)
        s["month"] = month
        rows.append(s)
    return pd.DataFrame(rows)


def agent_metrics(t: pd.DataFrame, agents: pd.DataFrame) -> pd.DataFrame:
    a = agents[["agent_id", "name", "team", "tier", "site", "shift"]].copy()
    # Agent IDs are the stable key; names are not used for joins.
    rows = []
    for aid, g in t.groupby("agent_id"):
        cs = g[g["csat_response"]]
        rows.append({
            "agent_id": aid,
            "tickets": len(g),
            "csat_responses": len(cs),
            "csat_response_rate_pct": len(cs) / len(g) * 100 if len(g) else np.nan,
            "mean_csat": cs["csat_score"].mean() if len(cs) else np.nan,
            "top_box_csat_pct": cs["top_box"].mean() * 100 if len(cs) else np.nan,
            "median_handle_time_min": g["handle_time_minutes"].median(),
            "sla_breach_rate_pct": g["sla_breach"].mean() * 100,
            "replacement_count": int(g["replacement_issued_bool"].sum()),
            "replacement_rate_pct": g["replacement_issued_bool"].mean() * 100,
            "replacement_cost_inr": g["replacement_cost_inr"].sum(),
        })
    m = pd.DataFrame(rows).merge(a, on="agent_id", how="left")
    # Relevant benchmark is the same team, same tier, same full analysis period.
    benchmarks = (
        m[m["tier"] == 1]
        .groupby("team")
        .agg(team_top_box_csat_pct=("top_box_csat_pct", lambda x: np.average(x.dropna(), weights=m.loc[x.dropna().index, "csat_responses"]) if x.notna().any() else np.nan))
        .reset_index()
    )
    # More directly calculate pooled benchmark from tickets to avoid agent-weighting artifacts.
    team_rows = []
    for team, g in t.merge(a[["agent_id","tier","team"]], on="agent_id", how="left").query("tier == 1").groupby("team"):
        cs = g[g["csat_response"]]
        team_rows.append({"team": team, "team_top_box_csat_pct": cs["top_box"].mean()*100 if len(cs) else np.nan})
    benchmarks = pd.DataFrame(team_rows)
    m = m.merge(benchmarks, on="team", how="left")
    m["csat_gap_vs_team_pp"] = m["top_box_csat_pct"] - m["team_top_box_csat_pct"]
    m["training_flag"] = False
    return m.sort_values(["tier", "top_box_csat_pct"], na_position="last").reset_index(drop=True)


def raw_bottom_ten(agent_df: pd.DataFrame, min_responses: int = 100) -> pd.DataFrame:
    x = agent_df[(agent_df["tier"] == 1) & (agent_df["csat_responses"] >= min_responses)].copy()
    return x.sort_values(["top_box_csat_pct", "csat_responses"], ascending=[True, False]).head(10).reset_index(drop=True)


def training_candidates(agent_df: pd.DataFrame, min_responses: int = 100) -> pd.DataFrame:
    x = agent_df[(agent_df["tier"] == 1) & (agent_df["csat_responses"] >= min_responses)].copy()
    # This is a filter, not a quality score: candidates have a meaningful sample and are below their own team's benchmark.
    x = x[x["csat_gap_vs_team_pp"] < 0].copy()
    x["priority_reason"] = x.apply(
        lambda r: f"{r['top_box_csat_pct']:.1f}% top-box CSAT, {abs(r['csat_gap_vs_team_pp']):.1f}pp below {r['team']} benchmark; {int(r['csat_responses'])} CSAT responses.", axis=1
    )
    return x.sort_values(["csat_gap_vs_team_pp", "top_box_csat_pct"]).reset_index(drop=True)
