from src.ai_classifier import dissatisfaction_driver, sentiment, apparent_resolution

def test_driver_and_sentiment():
    assert dissatisfaction_driver("Battery is not charging and this is frustrating") == "battery_charging"
    assert sentiment("This is terrible and I want a refund") == "negative"

def test_resolution():
    assert apparent_resolution("Refund initiated and ticket resolved") == "appears_resolved"
    assert apparent_resolution("Awaiting courier response") == "appears_pending"
