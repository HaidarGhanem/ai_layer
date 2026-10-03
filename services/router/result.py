from typing import Literal 
from pydantic import BaseModel

class RouterResult(BaseModel): 
    route: Literal["rag","chat","loop"]
    confidence: float 
    needs_clarification: bool