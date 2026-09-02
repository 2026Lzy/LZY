
"""
NASA C-MAPSS 数据集预处理脚本
对应项目：基于多智能算法的机械设备故障预测与运维决策系统
功能：数据清洗、特征工程、RUL标签构造、数据集划分、标准化
修复点：
1. 修复 sep="\s+" 转义警告，改为原始字符串 r"\s+"
2. 基于脚本位置计算绝对路径，避免相对路径文件找不到
3. 自动区分 26列数据文件 / 1列RUL标签文件，解决长度不匹配报错
4. 兼容官方测试集 + 独立RUL真值文件
5. 增加文件存在性校验、编码兼容，避免乱码崩溃
6. 特征清洗增加边界保护，std=0 时不做截断
7. 全局固定随机种子，结果可复现
8. 质量报告时间格式化，输出更规范
"""
import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# 全局固定随机种子，保证每次运行结果一致
np.random.seed(42)

# ===================== 路径配置（基于脚本绝对路径，不受运行目录影响） =====================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw", "cmapss")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

# ===================== 业务参数 =====================
SUBSET = "FD001"
RUL_MAX = 125        # RUL分段线性上限
FAULT_THRESHOLD = 30  # 故障阈值：最后30周期标记为故障

# 26列标准字段（C-MAPSS官方格式）
SENSOR_COLS = [f"s{i}" for i in range(1, 22)]
SETTING_COLS = ["setting1", "setting2", "setting3"]
ALL_COLS = ["unit", "cycle"] + SETTING_COLS + SENSOR_COLS


def load_data(filename):
    """读取原始txt文件，兼容编码，自动区分数据文件与RUL标签文件"""
    file_path = os.path.join(RAW_DIR, filename)

    # 文件存在性校验
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到文件：{file_path}\n请确认数据集已放入 data/raw/cmapss/ 目录")

    # 读取数据，兼容Windows中文编码
    try:
        df = pd.read_csv(file_path, sep=r"\s+", header=None, encoding="gbk")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, sep=r"\s+", header=None, encoding="utf-8", engine="python")

    # 自动区分RUL标签文件（1列）和数据文件（26列）
    if "rul_" in filename.lower():
        df.columns = ["rul"]
    else:
        if df.shape[1] != len(ALL_COLS):
            raise ValueError(f"文件列数异常：{filename} 实际{df.shape[1]}列，预期{len(ALL_COLS)}列")
        df.columns = ALL_COLS

    return df


def clean_features(df):
    """特征筛选与清洗，剔除无方差传感器，3σ异常值截断"""
    # 只保留真实存在的传感器列
    exist_sensors = [col for col in SENSOR_COLS if col in df.columns]
    if len(exist_sensors) == 0:
        raise ValueError("未找到有效传感器列")

    # 剔除方差接近0的常量传感器
    var = df[exist_sensors].var()
    valid_sensors = var[var > 1e-4].index.tolist()

    # 3σ异常值截断，std=0时跳过
    for col in valid_sensors:
        mean = df[col].mean()
        std = df[col].std()
        if std > 1e-6:
            df[col] = df[col].clip(mean - 3 * std, mean + 3 * std)

    return df[["unit", "cycle"] + valid_sensors], valid_sensors


def build_train_labels(df):
    """构造训练集RUL标签和故障分类标签（训练集有完整全生命周期）"""
    # 计算每个单元的最大周期
    max_cycles = df.groupby("unit")["cycle"].max().reset_index()
    max_cycles.columns = ["unit", "max_cycle"]

    df = df.merge(max_cycles, on="unit")
    df["rul"] = df["max_cycle"] - df["cycle"]

    # 分段线性RUL截断
    df["rul"] = df["rul"].clip(upper=RUL_MAX)

    # 故障分类标签
    df["fault"] = (df["rul"] <= FAULT_THRESHOLD).astype(int)

    df = df.drop("max_cycle", axis=1)
    return df


def build_test_labels(df_test, df_rul):
    """构造测试集标签（测试集RUL由独立RUL文件给出）"""
    # RUL文件第i行对应第i个发动机，unit从1开始
    df_rul = df_rul.copy()
    df_rul["unit"] = np.arange(1, len(df_rul)+1)
    df_rul.rename(columns={"rul":"final_rul"},inplace=True)

    # 计算每个发动机最大cycle
    max_cycles = df_test.groupby("unit")["cycle"].max().reset_index()
    max_cycles.columns = ["unit", "max_cycle"]

    # 两次merge，先合并max_cycle，再合并final_rul
    df = df_test.merge(max_cycles, on="unit", how="left")
    df = df.merge(df_rul[["unit","final_rul"]], on="unit", how="left")

    # 计算RUL
    df["rul"] = df["final_rul"] + (df["max_cycle"] - df["cycle"])

    # 分段线性截断
    df["rul"] = df["rul"].clip(upper=RUL_MAX)

    # 故障分类标签
    df["fault"] = (df["rul"] <= FAULT_THRESHOLD).astype(int)

    df = df.drop(["max_cycle", "final_rul"], axis=1)
    return df


def split_by_unit(df, train_ratio=0.8):
    """按发动机单元划分训练/验证集，避免时间序列数据泄露"""
    units = df["unit"].unique()
    n_units = len(units)

    n_train = int(n_units * train_ratio)
    shuffled = np.random.permutation(units)

    train_units = shuffled[:n_train]
    val_units = shuffled[n_train:]

    train_df = df[df["unit"].isin(train_units)].reset_index(drop=True)
    val_df = df[df["unit"].isin(val_units)].reset_index(drop=True)

    return train_df, val_df


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # ========== 1. 处理训练集 ==========
    print(f"加载 {SUBSET} 训练集...")
    train_raw = load_data(f"train_{SUBSET.lower()}.txt")
    train_clean, feature_cols = clean_features(train_raw)
    print(f"筛选后有效特征数：{len(feature_cols)}")

    train_labeled = build_train_labels(train_clean)

    # 按单元划分训练集 / 验证集
    train_df, val_df = split_by_unit(train_labeled, train_ratio=0.8)
    print(f"训练集划分 - 训练:{len(train_df)} 验证:{len(val_df)}")

    # 标准化（仅用训练集拟合）
    scaler = StandardScaler()
    train_df[feature_cols] = scaler.fit_transform(train_df[feature_cols])
    val_df[feature_cols] = scaler.transform(val_df[feature_cols])

    # ========== 2. 处理官方测试集 ==========
    print(f"加载 {SUBSET} 测试集与RUL真值...")
    test_raw = load_data(f"test_{SUBSET.lower()}.txt")
    test_clean, _ = clean_features(test_raw)

    rul_raw = load_data(f"RUL_{SUBSET}.txt")
    test_labeled = build_test_labels(test_clean, rul_raw)

    # 用训练集标准化器转换测试集
    test_df = test_labeled.copy()
    test_df[feature_cols] = scaler.transform(test_df[feature_cols])
    print(f"官方测试集样本数：{len(test_df)}")

    # ========== 3. 保存输出文件 ==========
    train_df.to_csv(os.path.join(PROCESSED_DIR, "train.csv"), index=False, encoding="utf-8-sig")
    val_df.to_csv(os.path.join(PROCESSED_DIR, "val.csv"), index=False, encoding="utf-8-sig")
    test_df.to_csv(os.path.join(PROCESSED_DIR, "test.csv"), index=False, encoding="utf-8-sig")

    # 保存标准化器
    with open(os.path.join(PROCESSED_DIR, "scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)

    # ========== 4. 生成索引文件 ==========
    index = {
        "subset": SUBSET,
        "feature_columns": feature_cols,
        "train_samples": len(train_df),
        "val_samples": len(val_df),
        "test_samples": len(test_df),
        "rul_max": RUL_MAX,
        "fault_threshold": FAULT_THRESHOLD,
        "files": ["train.csv", "val.csv", "test.csv", "scaler.pkl", "data_report.md"]
    }
    with open(os.path.join(PROCESSED_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    # ========== 5. 生成质量报告 ==========
    report_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""# 数据预处理质量报告
## 基本信息
- 数据集：NASA C-MAPSS {SUBSET}
- 预处理时间：{report_time}
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
- 特征标准化：StandardScaler（仅训练集拟合）
- 划分方式：训练/验证按发动机单元划分，无数据泄露；测试集为官方独立测试集
"""
    with open(os.path.join(PROCESSED_DIR, "data_report.md"), "w", encoding="utf-8") as f:
        f.write(report)

    print("\n✅ 预处理完成，输出已保存至 data/processed/")
    print("输出文件：train.csv、val.csv、test.csv、scaler.pkl、index.json、data_report.md")


if __name__ == "__main__":
    main()
