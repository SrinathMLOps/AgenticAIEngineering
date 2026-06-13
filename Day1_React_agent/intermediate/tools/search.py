from duckduckgo_search import DDGS


TOOL_DEFINITION = {
    "name": "web_search",
    "description": (
        "Search the web for current information. Use this when you need facts, "
        "recent news, documentation, or anything you are not certain about."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query. Be specific and concise.",
            },
            "max_results": {
                "type": "integer",
                "description": "Number of results to return (default 5, max 10).",
                "default": 5,
            },
        },
        "required": ["query"],
    },
}


def run(query: str, max_results: int = 5) -> str:
    max_results = min(max_results, 10)
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append(f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n")

    if not results:
        return "No results found for that query."

    return "\n---\n".join(results)
