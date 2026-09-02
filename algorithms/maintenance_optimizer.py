def optimize_maintenance(unit: int, fault_label: int, fault_confidence: float, rul: int, device_weight: float = 0.5):
    """
    启发式运维优化算法：综合故障状态、剩余寿命、设备权重计算运维优先级
    输出：优先级分数、优先级等级、运维建议、备件建议
    """
    # 优先级分数 0~100，越高越紧急
    fault_score = fault_confidence * 40 if fault_label == 1 else 0
    rul_score = ((125 - min(rul, 125)) / 125) * 40
    weight_score = device_weight * 20
    priority = int(round(fault_score + rul_score + weight_score))
    
    # 优先级分级
    if priority >= 70:
        level = "紧急"
        suggestion = "立即停机检修，更换故障部件"
        spare_parts = "轴承套件、密封件、检测工具"
    elif priority >= 40:
        level = "重要"
        suggestion = "7天内计划停机维护，重点检查退化部件"
        spare_parts = "润滑油、滤芯、备用传感器"
    else:
        level = "一般"
        suggestion = "按正常周期巡检，持续监测状态"
        spare_parts = "常规耗材"
    
    return {
        "unit": unit,
        "priority": priority,
        "priority_level": level,
        "suggestion": suggestion,
        "spare_parts": spare_parts
    }

