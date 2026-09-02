from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from .database import Base

class FaultResult(Base):
    __tablename__ = "fault_results"
    id = Column(Integer, primary_key=True, index=True)
    unit = Column(Integer)
    fault_label = Column(Integer)
    confidence = Column(Float)
    create_time = Column(DateTime, default=datetime.utcnow)

class RULResult(Base):
    __tablename__ = "rul_results"
    id = Column(Integer, primary_key=True, index=True)
    unit = Column(Integer)
    rul_value = Column(Integer)
    risk_level = Column(String)
    create_time = Column(DateTime, default=datetime.utcnow)

class MaintenanceDecision(Base):
    __tablename__ = "maintenance_decisions"
    id = Column(Integer, primary_key=True, index=True)
    unit = Column(Integer)
    priority = Column(Integer)
    priority_level = Column(String)
    suggestion = Column(String)
    spare_parts = Column(String)
    create_time = Column(DateTime, default=datetime.utcnow)

