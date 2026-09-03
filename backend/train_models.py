import os
import sys
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# 14个特征列，和前端、模型严格对应
FEATURE_COLS = ['s2','s3','s4','s7','s8','s9','s11','s12','s13','s14','s15','s17','s20','s21']

def main():
    # 路径适配：脚本在backend里，数据在上一级的data目录
    train_path = '../data/processed/train.csv'
    model_dir = './models'
    
    if not os.path.exists(train_path):
        print(f"错误：找不到训练数据 {train_path}")
        print("请确认 data/processed/train.csv 文件存在")
        sys.exit(1)
    
    os.makedirs(model_dir, exist_ok=True)
    
    print("正在读取训练数据...")
    df = pd.read_csv(train_path)
    
    X = df[FEATURE_COLS].values
    y_fault = df['fault'].values
    y_rul = df['rul'].values
    
    # 数据标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print("正在训练故障分类模型...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_scaled, y_fault)
    
    print("正在训练寿命预测模型...")
    reg = RandomForestRegressor(n_estimators=100, random_state=42)
    reg.fit(X_scaled, y_rul)
    
    # 保存模型+标准化器
    with open(os.path.join(model_dir, 'fault_clf.pkl'), 'wb') as f:
        pickle.dump({'model': clf, 'scaler': scaler}, f)
    
    with open(os.path.join(model_dir, 'rul_reg.pkl'), 'wb') as f:
        pickle.dump({'model': reg, 'scaler': scaler}, f)
    
    print("="*40)
    print(f"训练完成！模型已保存到 {os.path.abspath(model_dir)}")
    print("生成文件：fault_clf.pkl、rul_reg.pkl")
    print("现在可以启动后端服务了")

if __name__ == '__main__':
    main()
