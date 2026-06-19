import pytest
from app.intelligence.categorizer import FeedbackCategorizer
from app.models.agent_run import FeedbackCorrection

def test_static_categorization():
    categorizer = FeedbackCategorizer()
    res = categorizer.categorize("The app keeps crashing with a 500 internal server error")
    assert res.category == "bug"

def test_dynamic_learning_loop():
    categorizer = FeedbackCategorizer()
    text = "The setup has a bug"
    
    # 1. Base categorization
    res_before = categorizer.categorize(text)
    assert res_before.category == "bug"
    
    # 2. Add correction mock data
    corr = FeedbackCorrection(
        field_corrected="category",
        old_value="bug",
        new_value="other"  # corrected to other/support
    )
    corrections = [(corr, "The setup has a bug")]
    
    # 3. Categorize with corrections
    res_after = categorizer.categorize(text, corrections=corrections)
    
    # In this case:
    # "bug" keyword in category "bug" is penalized (-0.75 from 3.0 to 2.25)
    # "setup" keyword in category "support" (other) is boosted (+0.75 from 2.0 to 2.75)
    # So support score (2.75) > bug score (2.25) -> category should change to support (other)!
    assert res_after.category == "support"
