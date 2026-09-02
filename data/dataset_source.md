# 原始数据集来源说明

## 数据集名称
NASA C-MAPSS 涡扇发动机退化仿真数据集
（Commercial Modular Aero-Propulsion System Simulation）

## 官方来源与有效链接
- 官方发布主页（PHM Society）：https://data.phmsociety.org/nasa/
- 直接下载地址（已验证可访问）：https://phm-datasets.s3.amazonaws.com/NASA/6.+Turbofan+Engine+Degradation+Simulation+Data+Set.zip
- 镜像备份（ModelScope）：https://modelscope.cn/datasets/AI4Manufacture/NASA_CMAPSS

## 数据集授权
公开开源数据集，可用于学术研究与课程设计，无涉密、无商业限制。

## 数据集内容与规模
本项目使用 **FD001 子集**（单工况单故障模式）作为核心验证数据，完整包含4个子集：
| 子集 | 训练发动机数 | 测试发动机数 | 传感器数量 | 工况模式 | 故障模式 |
|------|--------------|--------------|----------|--------|--------|
| FD001 | 100 | 100 | 21 | 1种 | 单故障（风扇/压气机退化） |
| FD002 | 260 | 259 | 21 | 6种 | 单故障 |
| FD003 | 100 | 100 | 21 | 1种 | 双故障 |
| FD004 | 249 | 248 | 21 | 6种 | 双故障 |

原始数据为txt格式，包含3个运行设置参数 + 21路传感器测量值，记录每台发动机从正常运行到故障的全生命周期时序数据。

## 仓库存放说明
因原始数据集总大小约44MB，为避免仓库体积过大，原始zip包不提交至仓库，仅保留本说明文件。
可通过上述链接下载后解压至 `data/raw/` 目录，即可运行预处理脚本复现全部结果。
