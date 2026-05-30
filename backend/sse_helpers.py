import json
from typing import Any


def format_sse(data: dict[str, Any]) -> str:
    """Format a dict as a Server-Sent Event (SSE) frame."""
    return f"data: {json.dumps(data)}\n\n"
