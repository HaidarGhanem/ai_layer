from dataclasses import dataclass
from llama_index.core import Document 

@dataclass
class DocumentService: 
    def create(
            self,
            text: str,
            metadata: dict | None = None
    ) -> Document:
        return Document(text=text, metadata=metadata or {})