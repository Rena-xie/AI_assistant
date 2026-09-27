"""Web search tool — live information without an API key.

The tool queries a public search engine over plain HTTP and returns the top
results (title + URL + snippet) as plain text, so the agent can answer
questions that need *current* information (news, weather, quotes, ...) that
the offline knowledge base does not cover.

No extra dependency is needed: ``requests`` is already installed, and the
result pages are parsed with regular expressions instead of adding a parser
library.

Backends (``WEB_SEARCH_BACKEND``):

* ``bing`` (default) — live results from Bing's HTML results page. Picked as
  default because it answers plain ``requests`` calls with result markup
  (``li.b_algo`` blocks) where DuckDuckGo returns a bot-check page.
* ``duckduckgo``      — live results from DuckDuckGo's HTML endpoint (same
  parsing approach); may hit an anti-bot challenge on some networks.
* ``mock``            — fixed offline placeholder, useful for demos or CI
  without network access.

``search()`` is the injectable seam: unit tests replace ``search`` or
``get_backend`` to keep the whole test suite offline and deterministic.
"""

from __future__ import annotations

import re
from html import unescape as html_unescape
from urllib.parse import parse_qs, urlparse

import requests
from langchain_core.tools import tool

from ..config import WEB_SEARCH_BACKEND


BING_ENDPOINT = "https://www.bing.com/search"
DDG_ENDPOINT = "https://html.duckduckgo.com/html/"

# Same as a plain desktop browser, so the search engine serves the normal
# results page instead of a bot-check / compressed mobile layout.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

MAX_RESULTS = 5

REQUEST_TIMEOUT_SECONDS = 15.0

# Bing result page: one ``b_algo`` block per hit. ``h2>a`` holds the title and
# the result URL, ``div.b_caption>p`` the description; a result page is flat
# enough that regexes work without a parser dependency.
BING_BLOCK_PATTERN = re.compile(
    r'<li[^>]*class="[^"]*b_algo[^"]*".*?</li>', re.DOTALL
)
BING_TITLE_PATTERN = re.compile(
    r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL
)
BING_SNIPPET_PATTERN = re.compile(
    r'<div class="b_caption"[^>]*>\s*<p[^>]*>(.*?)</p>', re.DOTALL
)

# DuckDuckGo results: title + link in ``result__a``, description in
# ``result__snippet``. The two come out in the same order, so the snippet of
# entry *i* is the snippet list entry *i*.
RESULT_A_PATTERN = re.compile(
    r'<a[^>]+class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
    re.DOTALL,
)
SNIPPET_PATTERN = re.compile(
    r'<a[^>]+class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>',
    re.DOTALL,
)
TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")

MOCK_RESULTS = (
    "1. Web Search Results (mock backend)\n"
    "   https://example.com/search\n"
    "   Offline placeholder — set WEB_SEARCH_BACKEND=bing or duckduckgo to "
    "search the live web."
)


def get_backend() -> str:
    """Return the search backend from ``WEB_SEARCH_BACKEND`` (bing default)."""

    return (WEB_SEARCH_BACKEND or "bing").strip().lower()


def clean_text(text: str) -> str:
    """Strip HTML tags and entities, then fold whitespace to single spaces."""

    text = TAG_PATTERN.sub("", text)
    text = html_unescape(text)

    return WHITESPACE_PATTERN.sub(" ", text).strip()


def clean_url(href: str) -> str:
    """Decode HTML entities and DuckDuckGo ``uddg`` redirect links."""

    href = html_unescape(href)

    query = parse_qs(urlparse(href).query)

    return query.get("uddg", [href])[0]


def parse_bing_results(html: str) -> list[dict[str, str]]:
    """Extract ``{title, url, snippet}`` entries from a Bing results page.

    Args:
        html: Raw response body of ``https://www.bing.com/search``.

    Returns:
        The search results as a list of dicts, in page order.
    """

    results: list[dict[str, str]] = []

    for block in BING_BLOCK_PATTERN.findall(html):
        title_match = BING_TITLE_PATTERN.search(block)

        if not title_match:
            continue

        url, title = title_match.groups()

        snippet = ""
        snippet_match = BING_SNIPPET_PATTERN.search(block)

        if snippet_match:
            snippet = clean_text(snippet_match.group(1))

        results.append(
            {
                "title": clean_text(title),
                "url": clean_url(url),
                "snippet": snippet,
            }
        )

    return results


def parse_results(html: str) -> list[dict[str, str]]:
    """Extract ``{title, url, snippet}`` entries from a DuckDuckGo page.

    Args:
        html: Raw response body of the DuckDuckGo HTML endpoint.

    Returns:
        The search results as a list of dicts, in page order.
    """

    titles = RESULT_A_PATTERN.findall(html)
    snippets = [clean_text(text) for text in SNIPPET_PATTERN.findall(html)]

    results: list[dict[str, str]] = []

    for index, (url, title) in enumerate(titles):
        snippet = snippets[index] if index < len(snippets) else ""

        results.append(
            {
                "title": clean_text(title),
                "url": clean_url(url),
                "snippet": snippet,
            }
        )

    return results


def render_results(query: str, results: list[dict[str, str]]) -> str:
    """Format search results as a numbered, readable string.

    Args:
        query: The search terms, only used in the empty-results message.
        results: Entries as returned by the ``parse_*`` functions.

    Returns:
        One block per result, or a short no-results message.
    """

    if not results:
        return f"No search results found for: {query}"

    blocks = []

    for index, item in enumerate(results, 1):
        blocks.append(
            f"{index}. {item['title']}\n"
            f"   {item['url']}\n"
            f"   {item['snippet']}"
        )

    return "\n\n".join(blocks)


def search_with_bing(query: str) -> str:
    """Run a live Bing search and return the top results as text."""

    try:
        response = requests.get(
            BING_ENDPOINT,
            params={"q": query},
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        results = parse_bing_results(response.text)[:MAX_RESULTS]
    except Exception as exc:  # a broken network must fail the search, not the agent
        return f"Web search failed: {exc}"

    return render_results(query, results)


def search_with_duckduckgo(query: str) -> str:
    """Run a live DuckDuckGo search and return the top results as text."""

    try:
        response = requests.get(
            DDG_ENDPOINT,
            params={"q": query},
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        results = parse_results(response.text)[:MAX_RESULTS]
    except Exception as exc:  # a broken network must fail the search, not the agent
        return f"Web search failed: {exc}"

    return render_results(query, results)


def search(query: str) -> str:
    """Run ``query`` with the configured backend and return a text summary.

    Args:
        query: The search terms.

    Returns:
        The rendered results, or a readable error / no-results message.
    """

    backend = get_backend()

    if backend == "mock":
        return MOCK_RESULTS

    if backend == "duckduckgo":
        return search_with_duckduckgo(query)

    return search_with_bing(query)


@tool
def web_search(query: str) -> str:
    """
    Search the web for current, up-to-date information.

    Use this tool when the user needs recent, real-world facts that the
    offline knowledge base does not cover — news, weather, prices, stock
    quotes, or anything that changes over time.

    Args:
        query:
            The search terms, e.g. "today's weather in Beijing".

    Returns:
        A short list of search results with title, URL and snippet.
    """

    return search(query)