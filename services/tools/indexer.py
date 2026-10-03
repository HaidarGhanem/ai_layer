from services.tools.catalog import ToolCatalog
from services.tools.document_builder import ToolDocumentBuilder
from services.ingestion.pipeline import IngestionService 

class ToolIndexer: 
    def __init__(
        self,
        catalog: ToolCatalog,
        document_builder: ToolDocumentBuilder,
        ingestion: IngestionService
    ):
        self.catalog = catalog
        self.document_builder = document_builder
        self.ingestion = ingestion

    def build_documents(self):
        documents = []
        for definition in self.catalog.get_all():
            document = self.document_builder.build(
                definition
            )
            documents.append(document)
        return documents
    
    def index(self):
        documents = self.build_documents()
        return self.ingestion.run(
            documents=documents
        )