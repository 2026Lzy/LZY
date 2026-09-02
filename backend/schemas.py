from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FaultPredictRequest(BaseModel):
    features: List[float]
    unit: Optional[int] = None

class FaultPredictResponse(BaseModel):
    fault_label: int
    confidence: float
    unit: Optional[int] = None

class RULPredictRequest(BaseModel):
    features: List[float]
    unit: Optional[int] = None

class RULPredictResponse(BaseModel):
    rul_value: int
    risk_level: str
    unit: Optional[int] = None

class MaintenanceRequest(BaseModel):
    unit: int
    fault_label: int
    fault_confidence: float
    rul: int
    device_weight: float = 0.5

class MaintenanceResponse(BaseModel):
    unit: int
    priority: int
    priority_level: str
    suggestion: str
    spare_parts: str

