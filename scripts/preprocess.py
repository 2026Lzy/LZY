
### 文件：`scripts/preprocess.py`（可直接运行）
```python
"""
NASA C-MAPSS 数据集预处理脚本
对应项目：基于多智能算法的机械设备故障预测与运维决策系统
功能：数据清洗、特征工程、RUL标签构造、数据集划分、标准化
"""
import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# 路径配置
RAW_DIR = "../data/raw/cmapss"
PROCESSED_DIR = "../data/processed"
SUBSET = "FD001"
RUL_MAX = 125  # RUL分段线性上限
FAULT_THRESHOLD = 30  # 故障阈值：最后30周期为故障

# 21个传感器列名
SENSOR_COLS = [f"s{i}" for i in range(1, 22)]
SETTING_COLS = ["setting1", "setting2", "setting3"]
ALL_COLS = ["unit", "cycle"] + SETTING_COLS + SENSOR_COLS


def load_data(filename):
    """读取原始txt文件"""
    file_path = os.path.join(RAW_DIR, filename)
    df = pd.read_csv(file_path, sep="\s+", header=None)
    df.columns = ALL_COLS[:df.shape[1]]
    return df


def clean_features(df):
    """特征筛选与清洗"""
    # 剔除方差接近0的常量传感器
    var = df[SENSOR_COLS].var()
    valid_sensors = var[var > 1e-4].index.tolist()
    
    # 异常值截断
    for col in valid_sensors:
        mean = df[col].mean()
        std = df[col].std()
        df[col] = df[col].clip(mean - 3 * std, mean + 3 * std)
    
    return df[["unit", "cycle"] + valid_sensors], valid_sensors


def build_labels(df):
    """构造RUL标签和故障分类标签"""
    # 计算每个单元的最大周期
    max_cycles = df.groupby("unit")["cycle"].max().reset_index()
    max_cycles.columns = ["unit", "max_cycle"]
    
    df = df.merge(max_cycles, on="unit")
    df["rul"] = df["max_cycle"] - df["cycle"]
    
    # 分段线性RUL
    df["rul"] = df["rul"].clip(upper=RUL_MAX)
    
    # 故障分类标签：最后FAULT_THRESHOLD个周期为故障
    df["fault"] = (df["rul"] <= FAULT_THRESHOLD).astype(int)
    
    df = df.drop("max_cycle", axis=1)
    return df


def split_by_unit(df, train_ratio=0.7, val_ratio=0.1):
    """按发动机单元划分数据集，避免数据泄露"""
    units = df["unit"].unique()
    n_units = len(units)
    
    n_train = int(n_units * train_ratio)
    n_val = int(n_units * val_ratio)
    
    np.random.seed(42)
    shuffled = np.random.permutation(units)
    
    train_units = shuffled[:n_train]
    val_units = shuffled[n_train:n_train + n_val]
    test_units = shuffled[n_train + n_val:]
    
    train_df = df[df["unit"].isin(train_units)]
    val_df = df[df["unit"].isin(val_units)]
    test_df = df[df["unit"].isin(test_units)]
    
    return train_df, val_df, test_df


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # 1. 读取训练集
    print(f"加载 {SUBSET} 训练集...")
    train_raw = load_data(f"train_{SUBSET.lower()}.txt")
    
    # 2. 特征清洗
    train_clean, feature_cols = clean_features(train_raw)
    print(f"筛选后有效特征数：{len(feature_cols)}")
    
    # 3. 构造标签
    train_labeled = build_labels(train_clean)
    
    # 4. 划分数据集
    train_df, val_df, test_df = split_by_unit(train_labeled)
    print(f"样本划分 - 训练:{len(train_df)} 验证:{len(val_df)} 测试:{len(test_df)}")
    
    # 5. 标准化（仅用训练集拟合）
    scaler = StandardScaler()
    train_df[feature_cols] = scaler.fit_transform(train_df[feature_cols])
    val_df[feature_cols] = scaler.transform(val_df[feature_cols])
    test_df[feature_cols] = scaler.transform(test_df[feature_cols])
    
    # 6. 保存输出
    train_df.to_csv(os.path.join(PROCESSED_DIR, "train.csv"), index=False)
    val_df.to_csv(os.path.join(PROCESSED_DIR, "val.csv"), index=False)
    test_df.to_csv(os.path.join(PROCESSED_DIR, "test.csv"), index=False)
    
    # 保存标准化器
    with open(os.path.join(PROCESSED_DIR, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)
    
    # 7. 生成索引文件
    index = {
        "subset": SUBSET,
        "feature_columns": feature_cols,
        "train_samples": len(train_df),
        "val_samples": len(val_df),
        "test_samples": len(test_df),
        "rul_max": RUL_MAX,
        "fault_threshold": FAULT_THRESHOLD,
        "files": [
            "train.csv", "val.csv", "test.csv",
            "scaler.pkl", "data_report.md"
        ]
    }
    with open(os.path.join(PROCESSED_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    # 8. 生成质量报告
    report = f"""# 数据预处理质量报告
## 基本信息
- 数据集：NASA C-MAPSS {SUBSET}
- 预处理时间：{pd.Timestamp.now()}
- 有效特征数：{len(feature_cols)}
- RUL上限：{RUL_MAX}
- 故障阈值：最后{FAULT_THRESHOLD}周期

## 样本统计
| 数据集 | 样本数 | 发动机数 | 故障样本占比 |
|--------|--------|----------|--------------|
| 训练集 | {len(train_df)} | {train_df['unit'].nunique()} | {train_df['fault'].mean():.2%} |
| 验证集 | {len(val_df)} | {val_df['unit'].nunique()} | {val_df['fault'].mean():.2%} |
| 测试集 | {len(test_df)} | {test_df['unit'].nunique()} | {test_df['fault'].mean():.2%} |

## 数据质量
- 缺失值：{train_df.isnull().sum().sum()} 条
- 重复行：{train_df.duplicated().sum()} 条
- 特征标准化：StandardScaler（训练集拟合）
- 划分方式：按发动机单元划分，无数据泄露
"""
    with open(os.path.join(PROCESSED_DIR, "data_report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    
    print("预处理完成，输出已保存至 data/processed/")


if __name__ == "__main__":
    main()
