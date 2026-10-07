import pytest
import tempfile
from quality_metrics import QualityEvaluator

def test_accuracy_calculation_perfect():
    """100% 통과"""
    evaluator = QualityEvaluator("task_a", ".")
    test_result = {"passed": True}
    accuracy = evaluator.calculate_accuracy(test_result, 4)
    assert accuracy == 100.0

def test_accuracy_calculation_partial():
    """부분 통과"""
    evaluator = QualityEvaluator("task_a", ".")
    test_result = {
        "passed": False,
        "stdout": "4 passed, 1 failed in 0.50s"
    }
    accuracy = evaluator.calculate_accuracy(test_result, 5)
    assert accuracy == 80.0

def test_complexity_score_task_a():
    """Task A는 복잡도 3"""
    evaluator = QualityEvaluator("task_a", ".")
    score = evaluator.calculate_complexity_score()
    assert score == 3

def test_complexity_score_task_c():
    """Task C는 복잡도 9"""
    evaluator = QualityEvaluator("task_c", ".")
    score = evaluator.calculate_complexity_score()
    assert score == 9
