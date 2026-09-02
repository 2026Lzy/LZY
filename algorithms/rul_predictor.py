import os
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models/rul_predictor.pkl")
_model = None

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_rul(features: list):
    """
    输入：14维传感器特征列表
    输出：(剩余寿命RUL, 风险等级)
    风险等级：高(RUL≤30)、中(30<RUL≤80)、低(RUL>80)
    """
    model = load_model()
    X = np.array(features).reshape(1, -1)
    rul = int(round(model.predict(X)[0]))
    rul = max(0, min(rul, 125))  # 约束到合理范围
    
    if rul <= 30:
        risk = "高风险"
    elif rul <= 80:
        risk = "中风险"
    else:
        risk = "低风险"
    
    return rul, risk

