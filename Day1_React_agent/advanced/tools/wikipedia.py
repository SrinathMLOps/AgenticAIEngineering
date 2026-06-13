"""
Simple — Wikipedia Tool
========================
Uses the wikipedia-api package (pip install Wikipedia-API).
"""
import wikipediaapi

TOOL_DEFINITION = {
    "name": "wikipedia_search",
    "description": (
        "Look up a topic on Wikipedia and return a plain-English summary. "
        "Use this for well-established facts, historical events, people, places, "
        "concepts, or anything that likely has a Wikipedia article."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic to look up on Wikipedia (e.g. 'Python programming language').",
            },
            "sentences": {
                "type": "integer",
                "description": "Number of summary sentences to return (default 5, max 15).",
                "default": 5,
            },
        },
        "required": ["topic"],
    },
}

_wiki = wikipediaapi.Wikipedia(
    user_agent="BareMetalReActAgent/1.0 (educational project; contact: agent@example.com)",
    language="en",
)


def run(topic: str, sentences: int = 5) -> str:
    sentences = min(max(int(sentences), 1), 15)
    page = _wiki.page(topic)

    if not page.exists():
        # Try a case-insensitive search via the search endpoint
        return f"No Wikipedia article found for: '{topic}'. Try a more specific term."

    # Truncate summary to the requested number of sentences
    parts = page.summary.split(". ")
    excerpt = ". ".join(parts[:sentences]).strip()
    if not excerpt.endswith("."):
        excerpt += "."

    return f"Wikipedia — {page.title}\nURL: {page.fullurl}\n\n{excerpt}"
