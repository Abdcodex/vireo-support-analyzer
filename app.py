import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd
import streamlit as st
from src.data_loader import load_data
from src.metrics import prepare_tickets, summary_metrics, agent_metrics, raw_bottom_ten, training_candidates
from src.analysis import run

st.set_page_config(page_title="Vireo Audio Support Analytics", page_icon="🎧", layout="wide")

@st.cache_data
def load_all():
    tickets, agents, orders, customers, products = load_data()
    t = prepare_tickets(tickets, products)
    return t, agents, orders, customers, products

@st.cache_data
def load_outputs():
    root=Path(__file__).resolve().parent
    outs={}
    for n in ["monthly_metrics","period_metrics","agent_metrics","raw_bottom_ten","training_candidates","training_focus","classified_tickets","validation_results"]:
        p=root/"outputs"/f"{n}.csv"
        if p.exists(): outs[n]=pd.read_csv(p)
    return outs

t, agents, orders, customers, products = load_all()
outs=load_outputs()
if not outs:
    with st.spinner("Generating analysis outputs..."):
        run()
    st.cache_data.clear(); outs=load_outputs()

st.sidebar.title("Vireo Audio")
st.sidebar.caption("Support Tickets — Set B, Task 1 V4")
page=st.sidebar.radio("View",["Executive Overview","Agent Dashboard","Raw Bottom Ten","Training Priorities","AI Insights","Methodology & Limitations"])

if page=="Executive Overview":
    st.title("Customer Support Executive Overview")
    m=summary_metrics(t)
    cols=st.columns(8)
    labels=[("Tickets",m['tickets']),('CSAT responses',m['csat_responses']),("Response rate",f"{m['csat_response_rate_pct']:.1f}%"),("Top-box CSAT",f"{m['top_box_csat_pct']:.1f}%"),("Median handle",f"{m['median_handle_time_min']:.0f} min"),("SLA breach",f"{m['sla_breach_rate_pct']:.1f}%"),("Replacement rate",f"{m['replacement_rate_pct']:.1f}%"),("Replacement cost",f"₹{m['replacement_cost_inr']:,.0f}")]
    for c,(lab,val) in zip(cols,labels): c.metric(lab,val)
    st.subheader("Monthly trend")
    monthly=outs['monthly_metrics'].copy(); monthly['month']=pd.to_datetime(monthly['month'])
    c1,c2,c3=st.columns(3)
    with c1: st.caption("Top-box CSAT (%)"); st.line_chart(monthly.set_index('month')['top_box_csat_pct'])
    with c2: st.caption("Median handle time (minutes)"); st.line_chart(monthly.set_index('month')['median_handle_time_min'])
    with c3: st.caption("Replacement rate (%)"); st.line_chart(monthly.set_index('month')['replacement_rate_pct'])
    st.subheader("Period comparison")
    st.dataframe(outs['period_metrics'].style.format({"top_box_csat_pct":"{:.1f}%","median_handle_time_min":"{:.0f}","replacement_rate_pct":"{:.1f}%","replacement_cost_inr":"₹{:,.0f}"}),use_container_width=True,hide_index=True)
    st.info("Interpretation: CSAT is a survey outcome, not a causal measure of agent quality. Queue mix, survey response bias and legacy timestamp handling are explicit limitations.")

elif page=="Agent Dashboard":
    st.title("Agent Dashboard")
    x=outs['agent_metrics'].copy()
    c1,c2,c3,c4=st.columns(4)
    tiers=c1.multiselect("Tier",sorted(x.tier.unique()),default=sorted(x.tier.unique()))
    teams=c2.multiselect("Team",sorted(x.team.unique()),default=sorted(x.team.unique()))
    agents_sel=c3.multiselect("Agent",sorted(x.name.unique()))
    min_resp=c4.number_input("Minimum CSAT responses",0,1000,100)
    x=x[x.tier.isin(tiers)&x.team.isin(teams)&(x.csat_responses>=min_resp)]
    if agents_sel: x=x[x.name.isin(agents_sel)]
    cols=['agent_id','name','tier','team','tickets','csat_responses','top_box_csat_pct','team_top_box_csat_pct','csat_gap_vs_team_pp','median_handle_time_min','sla_breach_rate_pct','replacement_rate_pct','replacement_cost_inr']
    st.dataframe(x[cols].style.format({"top_box_csat_pct":"{:.1f}%","team_top_box_csat_pct":"{:.1f}%","csat_gap_vs_team_pp":"{:+.1f}pp","median_handle_time_min":"{:.0f}","sla_breach_rate_pct":"{:.1f}%","replacement_rate_pct":"{:.1f}%","replacement_cost_inr":"₹{:,.0f}"}),use_container_width=True,hide_index=True)

elif page=="Raw Bottom Ten":
    st.title("Raw Bottom Ten — requested client view")
    st.warning("Raw ranking is retained to answer the request. It is not automatically a training recommendation; Tier 2 is excluded from the Tier 1 comparison and queue mix is a known confounder.")
    b=outs['raw_bottom_ten']
    st.dataframe(b[['agent_id','name','team','csat_responses','top_box_csat_pct','median_handle_time_min','replacement_rate_pct','team_top_box_csat_pct','csat_gap_vs_team_pp']].style.format({"top_box_csat_pct":"{:.1f}%","team_top_box_csat_pct":"{:.1f}%","csat_gap_vs_team_pp":"{:+.1f}pp","median_handle_time_min":"{:.0f}","replacement_rate_pct":"{:.1f}%"}),use_container_width=True,hide_index=True)

elif page=="Training Priorities":
    st.title("Training Priorities — evidence view")
    st.write("Candidates require at least 100 CSAT responses and below-benchmark top-box CSAT within their Tier 1 team. This is a screening view, not a causal quality score.")
    focus=outs['training_focus']
    st.subheader("Focused review set")
    st.write("These four agents are the Chat Frontline members in the requested raw bottom-ten. They are surfaced for manager review because the email's queue-mix warning is less directly applicable than it is to hardware/warranty queues. This is not an automatic retraining verdict.")
    st.dataframe(focus[['agent_id','name','team','tickets','csat_responses','top_box_csat_pct','team_top_box_csat_pct','csat_gap_vs_team_pp','median_handle_time_min','replacement_rate_pct','replacement_cost_inr','focus_reason']].style.format({"top_box_csat_pct":"{:.1f}%","team_top_box_csat_pct":"{:.1f}%","csat_gap_vs_team_pp":"{:+.1f}pp","median_handle_time_min":"{:.0f}","replacement_rate_pct":"{:.1f}%","replacement_cost_inr":"₹{:,.0f}"}),use_container_width=True,hide_index=True)
    st.subheader("Other below-benchmark Tier 1 agents")
    c=outs['training_candidates']
    st.dataframe(c[~c.agent_id.isin(focus.agent_id)][['agent_id','name','team','tickets','csat_responses','top_box_csat_pct','team_top_box_csat_pct','csat_gap_vs_team_pp','median_handle_time_min','replacement_rate_pct','replacement_cost_inr']].style.format({"top_box_csat_pct":"{:.1f}%","team_top_box_csat_pct":"{:.1f}%","csat_gap_vs_team_pp":"{:+.1f}pp","median_handle_time_min":"{:.0f}","replacement_rate_pct":"{:.1f}%","replacement_cost_inr":"₹{:,.0f}"}),use_container_width=True,hide_index=True)

elif page=="AI Insights":
    st.title("AI-assisted ticket insights")
    v=outs['validation_results']
    st.subheader("Validation")
    st.dataframe(v,use_container_width=True,hide_index=True)
    c=outs['classified_tickets']
    st.subheader("AI/ML issue distribution")
    st.bar_chart(c['primary_issue_ai'].value_counts())
    st.subheader("Dissatisfaction drivers")
    st.bar_chart(c['dissatisfaction_driver_ai'].value_counts())
    st.subheader("Sentiment")
    st.bar_chart(c['customer_sentiment_ai'].value_counts())
    st.caption("The issue classifier is validated against the existing intake category as a proxy label. Dissatisfaction-driver, sentiment and apparent-resolution fields are heuristic assistance and require human review before being treated as gold labels.")
    st.dataframe(c[['ticket_id','category','primary_issue_ai','ai_confidence','customer_sentiment_ai','dissatisfaction_driver_ai','apparent_resolution_ai','customer_message','agent_notes']].head(100),use_container_width=True,hide_index=True)

else:
    st.title("Methodology & Limitations")
    st.markdown("""
**CSAT:** 1–5 survey; blank responses excluded. Top-box = 4 or 5.

**Handle time:** first human response to resolution. Legacy reconstructed resolution timestamps are shifted +05:30 because the policy says those legacy event-log timestamps are UTC while helpdesk display/export is IST. The raw data produced 2,309 negative handle times; after normalization there are zero.

**Tiering:** Tier 2 is retained but excluded from Tier 1 training ranking because the policy says Tier 2 should not be compared with Tier 1 on volume metrics and its work is measured differently.

**Queue mix:** The client email explicitly warns that hardware triage receives angrier customers by design. Therefore raw CSAT is not treated as causal evidence of agent quality.

**Replacement cost:** product unit cost + ₹340 logistics, per policy. Finance's ₹2,500 figure is not used for planning.

**AI:** local TF-IDF + LogisticRegression predicts intake category from ticket text; no per-ticket paid LLM calls. A prompt specification is included for optional future LLM use. The holdout accuracy is proxy validation against the intake category, not human gold-label validation.

**Deliberate omissions:** predictive performance scoring, causal modeling, customer profiling, lot-code analysis, and production deployment were omitted because they are not necessary to answer the stated support-dashboard problem and would create unsupported certainty or scope.
    """)
