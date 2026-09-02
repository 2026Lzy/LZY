from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import FaultPredictRequest, FaultPredictResponse
from ..models import FaultResult
from algorithms.fault_classifier import predict_fault

router = APIRouter(prefix="/api/fault", tags=["故障诊断"])

@router.post("/predict", response_model=FaultPredictResponse)
def fault_predict(request: FaultPredictRequest, db: Session = Depends(get_db)):
    label, confidence = predict_fault(request.features)
    result = FaultResult(unit=request.unit, fault_label=label, confidence=confidence)
    db.add(result)
    db.commit()
    db.refresh(result)
    return FaultPredictResponse(fault_label=label, confidence=confidence, unit=request.unit)

@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    return db.query(FaultResult).order_by(FaultResult.create_time.desc()).limit(20).all()

