import os

TOOL_DEFINITION = {
    "name": "file_io",
    "description": (
        "Read from or write to a local file. "
        "Use 'read' to get file contents and 'write' to save results or notes. "
        "Files are saved in the current working directory."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["read", "write"],
                "description": "Whether to read or write a file.",
            },
            "filename": {
                "type": "string",
                "description": "The filename (e.g. 'output.txt', 'notes.md').",
            },
            "content": {
                "type": "string",
                "description": "Content to write. Required when action is 'write'.",
            },
        },
        "required": ["action", "filename"],
    },
}


def run(action: str, filename: str, content: str = "") -> str:
    # Prevent path traversal
    safe_filename = os.path.basename(filename)

    if action == "read":
        if not os.path.exists(safe_filename):
            return f"File not found: {safe_filename}"
        with open(safe_filename, "r", encoding="utf-8") as f:
            return f.read()

    if action == "write":
        if not content:
            return "No content provided to write."
        with open(safe_filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Written {len(content)} characters to {safe_filename}"

    return f"Unknown action: {action}. Use 'read' or 'write'."
