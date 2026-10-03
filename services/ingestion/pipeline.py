from llama_index.core.ingestion import IngestionPipeline

class IngestionService:
    def __init__(self, transformations=None):
        transformations = transformations or []

        self.pipeline = IngestionPipeline(
            transformations=transformations
        )

    def run(self, documents):
        return self.pipeline.run(documents=documents)

