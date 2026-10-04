import hashlib 

class ToolIdentity:

    def build(self, name:str, metadata: dict) -> str:
        source = metadata.get("source","default")
        raw_identity = f"{source}:{name}"
        return raw_identity

    def document_id(self, tool_id:str) -> str:
        return (
            "tool:"
            + hashlib.sha256(
                tool_id.encode("utf-8")
            ).hexdigest()
        )