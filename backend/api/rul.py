from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import RULPredictRequest, RULPredictResponse
from ..models import RULResult
from algorithms.rul_predictor import predict_rul

router = APIRouter(prefix="/api/rul", tags=["寿命预测"])

@router.post("/predict", response_model=RULPredictResponse)
def rul_predict(request: RULPredictRequest, db: Session = Depends(get_db)):
    rul, risk = predict_rul(request.features)
    result = RULResult(unit=request.unit, rul_value=rul, risk_level=risk)
    db.add(result)
    db.commit()
    db.refresh(result)
    return RULPredictResponse(rul_value=rul, risk_level=risk, unit=request.unit)

@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    return db.query(RULResult).order_by(RULResult.create_time.desc()).limit(20).all()

