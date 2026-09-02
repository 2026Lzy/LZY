基于多智能算法的机械设备故障预测与运维决策系统
## 项目简介

本项目为**制造智能技术课程设计**成果，面向工业设备运维场景，构建了完整的 "状态感知 - 故障诊断 - 寿命预测 - 运维决策" 智能业务闭环。系统采用 B/S 架构，集成机器学习故障分类、时序剩余寿命预测、启发式运维优化决策三大核心算法，覆盖课程至少 3 项技术方向，可直接运行演示。

项目采用**Vibe Coding（AI 辅助编程）**模式开发，全程留存开发过程档案，遵循小步 Git 提交规范，满足课程过程考核要求。

## 项目背景

工业设备意外故障停机是造成生产损失的核心原因，传统定期检修模式普遍存在过维修或欠维修问题。本项目以航空发动机退化场景为切入点，基于 NASA 公开工业数据集，运用制造智能课程所学技术，实现：

1. **智能故障诊断**：基于传感器数据自动识别设备故障状态
2. **智能寿命预测**：预测设备剩余使用寿命（RUL）并分级预警
3. **智能运维决策**：多维度综合评估生成运维优先级与处置方案

## 系统架构

采用标准四层 B/S 架构，前后端分离，数据全链路持久化：

```
前端UI层（浏览器）
    ↓ HTTP请求
后端服务层（FastAPI）
    ↓ 调用封装
算法模型层（故障分类 / RUL预测 / 运维优化）
    ↓ 读写
数据持久层（SQLite）
'''
# 数据来源说明

## 一、数据集基本信息

**数据集全称**：NASA C-MAPSS 涡扇发动机退化仿真数据集
（Commercial Modular Aero-Propulsion System Simulation，商用模块化航空推进系统仿真数据集）

该数据集由 NASA 艾姆斯研究中心发布，是工业预测性维护领域的标准公开数据集，模拟航空发动机从正常运行到性能退化直至故障的全生命周期时序数据，广泛用于故障诊断、剩余使用寿命（RUL）预测等制造智能技术研究。

## 二、官方来源与有效下载链接

### 1. 官方发布源（PHM 协会）

- 数据集官方主页：[https://data.phmsociety.org/nasa/](https://data.phmsociety.org/nasa/)
- 原始数据集直接下载地址（已验证可访问）：
[https://phm-datasets.s3.amazonaws.com/NASA/6.+Turbofan+Engine+Degradation+Simulation+Data+Set.zip](https://phm-datasets.s3.amazonaws.com/NASA/6.+Turbofan+Engine+Degradation+Simulation+Data+Set.zip)

### 2. 国内镜像源（推荐，下载速度更快）

- 魔搭 ModelScope 镜像：[https://modelscope.cn/datasets/AI4Manufacture/NASA_CMAPSS](https://modelscope.cn/datasets/AI4Manufacture/NASA_CMAPSS)
- 飞桨 AI Studio 镜像：[https://aistudio.baidu.com/datasetdetail/11724](https://aistudio.baidu.com/datasetdetail/11724)
