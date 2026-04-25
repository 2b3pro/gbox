import urllib.request
import urllib.parse
import re
from .fs import _clean_path

def fetch_url(url: str) -> str:
    """Fetches a URL as clean markdown via r.jina.ai. Falls back to raw HTML on failure."""
    u = _clean_path(url)
    if not re.match(r"^https?://", u):
        return f"Error: invalid URL: {u}"
    jina = "https://r.jina.ai/" + u
    for target in (jina, u):
        try:
            req = urllib.request.Request(target, headers={"User-Agent": "litert-preset/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read().decode("utf-8", errors="replace")
            if target == u:
                data = re.sub(r"<script[\s\S]*?</script>", "", data, flags=re.I)
                data = re.sub(r"<style[\s\S]*?</style>", "", data, flags=re.I)
                data = re.sub(r"<[^>]+>", "", data)
                data = re.sub(r"\n\s*\n+", "\n\n", data).strip()
            return data[:8_000]
        except Exception:
            continue
    return f"Error: failed to fetch {u}"

def web_search(query: str) -> str:
    """Searches the web via DuckDuckGo and returns result snippets.
    
    Args:
        query: The search terms.
    """
    q = urllib.parse.quote(query)
    # Using the 'lite' version of DDG which is scraper-friendly
    url = f"https://duckduckgo.com/lite/?q={q}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            # Extract links and snippets (rough extraction)
            results = re.findall(r'<a[^>]*class="result-link"[^>]*>(.*?)</a>.*?<td[^>]*class="result-snippet"[^>]*>(.*?)</td>', html, re.S)
            if not results:
                return "No results found."
            
            output = []
            for title, snippet in results[:8]:
                title = re.sub(r'<[^>]+>', '', title).strip()
                snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                output.append(f"Title: {title}\nSnippet: {snippet}\n---")
            return "\n".join(output)
    except Exception as e:
        return f"Error searching: {e}"

tools = [fetch_url, web_search]
