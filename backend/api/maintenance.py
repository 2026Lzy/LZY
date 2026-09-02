from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import MaintenanceRequest, MaintenanceResponse
from ..models import MaintenanceDecision
from algorithms.maintenance_optimizer import optimize_maintenance

router = APIRouter(prefix="/api/maintenance", tags=["运维决策"])

@router.post("/optimize", response_model=MaintenanceResponse)
def maintenance_optimize(request: MaintenanceRequest, db: Session = Depends(get_db)):
    result = optimize_maintenance(
        unit=request.unit,
        fault_label=request.fault_label,
        fault_confidence=request.fault_confidence,
        rul=request.rul,
        device_weight=request.device_weight
    )
    record = MaintenanceDecision(**result)
    db.add(record)
    db.commit()
    db.refresh(record)
    return result

@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    return db.query(MaintenanceDecision).order_by(MaintenanceDecision.priority.desc()).limit(20).all()

