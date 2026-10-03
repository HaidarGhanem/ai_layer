from services.tools.definition import ToolDefinition

class ToolCatalogBuilder:
    def build( self, tool ) -> ToolDefinition:

        input_schema = {}

        if hasattr(tool, "args_schema") and tool.args_schema: 
            schema = tool.args_schema.model_json_schema()
            input_schema = schema

        return ToolDefinition(
            name=tool.name,
            description=tool.description,
            input_schema=input_schema
        )
    