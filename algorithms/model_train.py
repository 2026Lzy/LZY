import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

# 路径配置
DATA_PATH = "../data/processed/train.csv"
MODEL_DIR = "./models"
os.makedirs(MODEL_DIR, exist_ok=True)

def train():
    print("加载训练数据...")
    df = pd.read_csv(DATA_PATH)
    
    # 提取特征列（所有s开头的传感器列）
    feature_cols = [col for col in df.columns if col.startswith("s")]
    X = df[feature_cols]
    y_fault = df["fault"]
    y_rul = df["rul"]
    
    print(f"特征数：{len(feature_cols)}，训练样本数：{len(df)}")
    
    # 1. 训练故障分类模型
    print("训练故障分类模型...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y_fault)
    joblib.dump(clf, os.path.join(MODEL_DIR, "fault_classifier.pkl"))
    
    # 2. 训练RUL预测模型
    print("训练RUL预测模型...")
    reg = RandomForestRegressor(n_estimators=100, random_state=42)
    reg.fit(X, y_rul)
    joblib.dump(reg, os.path.join(MODEL_DIR, "rul_predictor.pkl"))
    
    print("模型训练完成，已保存至 algorithms/models/")

if __name__ == "__main__":
    train()

