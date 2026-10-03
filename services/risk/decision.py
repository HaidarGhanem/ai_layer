from typing import Literal 
from pydantic import BaseModel
from services.risk.level import RiskLevel 

class RiskDecision(BaseModel):
    action: Literal['allow','confirm','reject']
    risk_level: RiskLevel
    reason: str