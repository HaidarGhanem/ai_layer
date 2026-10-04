from dataclasses import dataclass

from llama_index.core import Document


@dataclass
class DocumentService:

    def create(
        self,
        text: str,
        metadata: dict | None = None,
        document_id: str | None = None,
    ) -> Document:

        document_data = {
            "text": text,
            "metadata": metadata or {},
        }

        if document_id is not None:

            document_data["id_"] = document_id

        return Document(
            **document_data
        )