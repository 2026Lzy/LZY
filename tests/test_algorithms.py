import sys
sys.path.append(".")
from algorithms.fault_classifier import predict_fault
from algorithms.rul_predictor import predict_rul
from algorithms.maintenance_optimizer import optimize_maintenance

# 14维测试样本
test_features = [0.1]*14

def test_fault_classifier():
    label, conf = predict_fault(test_features)
    assert label in [0, 1]
    assert 0 <= conf <= 1

def test_rul_predictor():
    rul, risk = predict_rul(test_features)
    assert isinstance(rul, int)
    assert 0 <= rul <= 125
    assert risk in ["高风险", "中风险", "低风险"]

def test_maintenance_optimizer():
    result = optimize_maintenance(1, 1, 0.9, 25, 0.7)
    assert result["priority"] >= 0
    assert result["priority_level"] in ["紧急", "重要", "一般"]
    assert result["suggestion"]
    assert result["spare_parts"]

