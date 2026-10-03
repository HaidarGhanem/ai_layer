from dataclasses import dataclass
from typing import Optional 
from services.vectors.provider import VectorStoreProvider

@dataclass 
class VectorStoreConfiguration:
    provider: VectorStoreProvider
    collection_name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    table_name: Optional[str] = None 
    dimension: Optional[int] = 768