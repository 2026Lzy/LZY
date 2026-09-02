import os
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models/fault_classifier.pkl")
_model = None

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_fault(features: list):
    """
    输入：14维传感器特征列表
    输出：(故障标签 0=正常 1=故障, 置信度)
    """
    model = load_model()
    X = np.array(features).reshape(1, -1)
    label = int(model.predict(X)[0])
    confidence = float(model.predict_proba(X)[0].max())
    return label, round(confidence, 4)

