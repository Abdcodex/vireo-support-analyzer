import pandas as pd
from src.metrics import prepare_tickets, summary_metrics, raw_bottom_ten


def test_legacy_timestamp_normalization_removes_negative_handle_time():
    tickets = pd.DataFrame({
        "ticket_id":["1","2"], "created_at":["2025-01-01 08:00","2025-01-01 09:00"],
        "first_response_at":["2025-01-01 08:10","2025-01-01 09:10"],
        "resolved_at":["2025-01-01 08:40","2025-01-01 09:30"],
        "status":["resolved","resolved"], "channel":["chat","chat"], "customer_id":["c","d"], "order_id":[None,None],
        "product_sku":["s","s"], "category":["Other","Other"], "priority":["Normal","Normal"], "assigned_team":["Chat Frontline"]*2,
        "agent_id":["a","a"], "transfers":[0,0], "csat_score":[5,3], "refund_amount_inr":[None,None], "refund_reason_code":[None,None],
        "replacement_issued":["N","N"], "customer_message":["x","y"], "agent_notes":["resolved","resolved"], "source_system":["legacy_fd","helpdesk"]
    })
    products = pd.DataFrame({"sku":["s"],"unit_cost_inr":[100]})
    out = prepare_tickets(tickets, products)
    assert out.loc[0,"handle_time_minutes"] == 360
    assert out.loc[1,"handle_time_minutes"] == 20
    assert (out.handle_time_minutes >= 0).all()


def test_csat_denominator_excludes_blank():
    tickets = pd.DataFrame({
        "ticket_id":["1","2","3"], "created_at":["2025-01-01"]*3, "first_response_at":["2025-01-01"]*3,
        "resolved_at":["2025-01-01"]*3, "status":["resolved"]*3, "channel":["chat"]*3, "customer_id":["a","b","c"], "order_id":[None]*3,
        "product_sku":["s"]*3, "category":["Other"]*3, "priority":["Normal"]*3, "assigned_team":["Chat Frontline"]*3, "agent_id":["a"]*3,
        "transfers":[0]*3, "csat_score":[5,1,None], "refund_amount_inr":[None]*3, "refund_reason_code":[None]*3,
        "replacement_issued":["N"]*3, "customer_message":["x"]*3, "agent_notes":["resolved"]*3, "source_system":["helpdesk"]*3
    })
    products = pd.DataFrame({"sku":["s"],"unit_cost_inr":[100]})
    m = summary_metrics(prepare_tickets(tickets,products))
    assert m["csat_responses"] == 2
    assert m["csat_response_rate_pct"] == 2/3*100
    assert m["top_box_csat_pct"] == 50
