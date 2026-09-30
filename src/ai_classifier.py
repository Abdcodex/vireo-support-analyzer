import json
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

DRIVER_PATTERNS = {
    "delivery_delay": r"\b(delay|delayed|late|tracking|courier|delivery|not delivered|shipment|awb)\b",
    "product_fault": r"\b(not working|doesn.?t work|dead|broken|fault|issue|problem|stopped|damaged|defect)\b",
    "battery_charging": r"\b(battery|charge|charging|charges|charging case|drain)\b",
    "audio_quality": r"\b(sound|audio|volume|noise|mic|microphone|hear|hearing|call quality|distortion)\b",
    "connectivity": r"\b(bluetooth|connect|connection|pair|pairing|disconnect|wifi)\b",
    "refund_return": r"\b(refund|return|returned|money back|pickup)\b",
    "billing_payment": r"\b(payment|paid|charge|charged|invoice|billing|coupon|price)\b",
    "account_login": r"\b(login|log in|account|password|otp|sign in)\b",
    "firmware_app": r"\b(app|firmware|update|software)\b",
    "customer_service": r"\b(rude|agent|support|service|experience|waiting|no response|called)\b",
}


def dissatisfaction_driver(text: str) -> str:
    s = str(text).lower()
    hits = [k for k, p in DRIVER_PATTERNS.items() if re.search(p, s)]
    return hits[0] if hits else "unclear"


def sentiment(text: str) -> str:
    s = str(text).lower()
    neg = ["angry", "pathetic", "terrible", "worst", "hate", "useless", "frustrated", "disappointed", "ridiculous", "bad", "poor", "not working", "refund"]
    pos = ["thanks", "thank you", "great", "good", "happy", "helpful", "resolved"]
    n, p = sum(w in s for w in neg), sum(w in s for w in pos)
    if n > p and n > 0: return "negative"
    if p > n and p > 0: return "positive"
    return "neutral_or_unclear"


def apparent_resolution(notes: str) -> str:
    s = str(notes).lower()
    if any(w in s for w in ["refund initiated", "replacement", "reship", "resolved", "fixed", "updated", "credited", "closed"]):
        return "appears_resolved"
    if any(w in s for w in ["pending", "awaiting", "escalated", "follow up", "follow-up", "awaiting"]):
        return "appears_pending"
    return "unclear"


def build_model(train_df: pd.DataFrame):
    x = (train_df["customer_message"].fillna("") + " " + train_df["agent_notes"].fillna(""))
    y = train_df["category"].fillna("Other")
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=2, max_features=20000, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ]).fit(x, y)


def classify_dataset(t: pd.DataFrame, sample_size: int = 1200):
    df = t.copy()
    usable = df[df["customer_message"].fillna("").str.len().gt(0)].copy()
    if len(usable) > sample_size:
        usable = usable.sample(sample_size, random_state=42)
    x = usable["customer_message"].fillna("") + " " + usable["agent_notes"].fillna("")
    y = usable["category"].fillna("Other")
    # Proxy validation: holdout against the intake category. This is NOT human gold-label validation.
    train_idx, test_idx = train_test_split(np.arange(len(usable)), test_size=0.25, random_state=42, stratify=y)
    train_df = usable.iloc[train_idx]
    test_df = usable.iloc[test_idx]
    model = build_model(train_df)
    pred = model.predict(test_df["customer_message"].fillna("") + " " + test_df["agent_notes"].fillna(""))
    proba = model.predict_proba(test_df["customer_message"].fillna("") + " " + test_df["agent_notes"].fillna(""))
    conf = proba.max(axis=1)
    acc = accuracy_score(test_df["category"], pred)

    out = usable.copy()
    out["primary_issue_ai"] = model.predict(x)
    out["ai_confidence"] = model.predict_proba(x).max(axis=1)
    out["customer_sentiment_ai"] = out["customer_message"].map(sentiment)
    out["dissatisfaction_driver_ai"] = (out["customer_message"].fillna("") + " " + out["agent_notes"].fillna("")).map(dissatisfaction_driver)
    out["apparent_resolution_ai"] = out["agent_notes"].map(apparent_resolution)
    out["ai_method"] = "TF-IDF + LogisticRegression (local, zero API cost)"

    report = classification_report(test_df["category"], pred, output_dict=True, zero_division=0)
    validation = pd.DataFrame([
        {"metric": "validation_sample_size", "value": int(len(test_df))},
        {"metric": "holdout_accuracy", "value": float(acc)},
        {"metric": "holdout_error_rate", "value": float(1-acc)},
        {"metric": "mean_test_confidence", "value": float(conf.mean())},
        {"metric": "failure_type", "value": "confusion among semantically similar intake categories; labels are proxy labels, not human-reviewed gold labels"},
        {"metric": "validation_note", "value": "This validates prediction against the existing intake category. A human review sample is still required to validate dissatisfaction-driver and resolution fields."},
        {"metric": "model", "value": "TF-IDF + LogisticRegression"},
        {"metric": "cost", "value": "₹0 API/model-call cost; runs locally"},
    ])
    return out, validation
