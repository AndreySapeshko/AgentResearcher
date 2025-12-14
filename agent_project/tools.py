def search_web(query: str) -> dict:
    return {
        "results": [
            f"https://example.com/search?q={query}",
            f"https://test.com/info/{query.replace(' ', '_')}"
        ]
    }


def fetch_url(url: str) -> dict:
    html = f"<html><body><h1>Fake page for {url}</h1></body></html>"
    return {"html": html}


def read_file(path: str) -> dict:
    with open(path, "r", encoding="utf8") as f:
        text = f.read()

    return {"text": text}


def write_file(path: str, content: str) -> dict:
    try:
        with open(path, "w", encoding="utf8") as f:
            f.write(content)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
