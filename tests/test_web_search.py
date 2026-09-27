"""Tests for the web_search tool — offline by default (no network call).

``search_with_bing`` / ``search_with_duckduckgo`` are the only functions that
touch the network and they are never executed here; the parsers are
unit-tested against canned HTML fragments instead. The live backend is
exercised end-to-end by the CLI evaluation (``python evals/run.py agent``).
"""

from __future__ import annotations

import requests
from importlib import import_module
from langchain_core.tools import BaseTool

from aila.tools import TOOLS
from aila.tools.web_search import (
    MOCK_RESULTS,
    clean_url,
    parse_bing_results,
    parse_results,
    render_results,
    search,
    search_with_bing,
    web_search,
)

# ``import aila.tools.web_search as x`` would bind ``x`` to the **tool**
# (``tools/__init__.py`` overwrites the package attribute ``tools.web_search``
# with the decorated function), so the module is reached explicitly.
web_search_module = import_module("aila.tools.web_search")

# The agent now ships exactly these three tools.
EXPECTED_TOOL_NAMES = {"calculator", "knowledge_search", "web_search"}

# Reduced sample of the Bing results page: the parser only reads ``li.b_algo``
# blocks (``h2>a`` for title + URL, ``div.b_caption>p`` for the snippet).
BING_SAMPLE_HTML = """
<ol id="b_results">
<li class="b_algo" data-id iid=SERP.5334>
  <div class="b_tpcn"><cite>https://example.com/langgraph</cite></div>
  <h2 class="">
    <a target="_blank" href="https://example.com/langgraph">
      <strong>LangGraph</strong>: Open Source AI Agent Framework
    </a>
  </h2>
  <div class="b_caption"><p class="b_lineclamp2">
    LangGraph is a library for building &amp; running stateful agents.
  </p></div>
</li>
<li class="b_algo" data-id iid=SERP.5335>
  <h2 class=""><a target="_blank" href="https://example.com/docs">Agents &amp; memory</a></h2>
  <div class="b_caption"><p class="b_lineclamp2">Agents combine tools and memory.</p></div>
</li>
</ol>
"""

# Reduced sample of the DuckDuckGo HTML endpoint markup: the parser only reads
# ``result__a`` (title + link) and ``result__snippet`` blocks.
DDG_SAMPLE_HTML = """
<div class="result__body">
  <h2 class="result__title">
    <a rel="nofollow" class="result__a" href="https://example.com/langgraph">
      LangGraph Overview
    </a>
  </h2>
  <a class="result__snippet" href="https://example.com/langgraph">
    LangGraph is a library for building stateful agents.
  </a>
</div>
<div class="result__body">
  <h2 class="result__title">
    <a rel="nofollow" class="result__a"
       href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fdocs">
       Stateful agents &amp; memory
    </a>
  </h2>
  <a class="result__snippet"
     href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fdocs">
     Agents combine tools, memory and an LLM.
  </a>
</div>
"""


def test_web_search_is_a_langchain_tool():
    assert isinstance(web_search, BaseTool)
    assert web_search.name == "web_search"
    assert "search" in web_search.description.lower()
    assert "current" in web_search.description.lower()


def test_web_search_is_registered_in_tools_registry():
    assert {tool.name for tool in TOOLS} == EXPECTED_TOOL_NAMES


def test_parse_bing_results_extracts_title_url_snippet():
    results = parse_bing_results(BING_SAMPLE_HTML)

    assert [result["title"] for result in results] == [
        "LangGraph: Open Source AI Agent Framework",
        "Agents & memory",
    ]
    assert results[0]["url"] == "https://example.com/langgraph"
    assert "stateful agents" in results[0]["snippet"].lower()


def test_parse_bing_results_skips_blocks_without_title():
    assert parse_bing_results('<li class="b_algo"><div class="b_caption"><p>x</p></div></li>') == []


def test_parse_results_extracts_title_url_snippet():
    results = parse_results(DDG_SAMPLE_HTML)

    assert [result["title"] for result in results] == [
        "LangGraph Overview",
        "Stateful agents & memory",
    ]
    assert results[0]["url"] == "https://example.com/langgraph"
    assert "agents combine tools" in results[1]["snippet"].lower()


def test_clean_url_decodes_uddg_redirect():
    encoded = "//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fdocs"

    assert clean_url(encoded) == "https://example.com/docs"


def test_render_results_is_numbered_and_readable():
    rendered = render_results(
        "agents",
        [{"title": "Title", "url": "https://example.com", "snippet": "Snippet"}],
    )

    assert rendered == "1. Title\n   https://example.com\n   Snippet"


def test_render_results_reports_empty_search():
    assert render_results("nothing", []) == "No search results found for: nothing"


def test_opts_into_mock_backend_only_via_setting(monkeypatch):
    monkeypatch.setattr(web_search_module, "get_backend", lambda: "mock")

    result = search("今天北京天气怎么样？")

    assert result == MOCK_RESULTS
    assert "mock" in result.lower()


def test_web_search_tool_uses_mock_backend(monkeypatch):
    monkeypatch.setattr(web_search_module, "get_backend", lambda: "mock")

    result = web_search.invoke("今天北京天气怎么样？")

    assert result == MOCK_RESULTS


def test_bing_failure_degrades_to_readable_message(monkeypatch):
    def boom(*args, **kwargs):
        raise requests.RequestException("timeout")

    monkeypatch.setattr(web_search_module.requests, "get", boom)

    result = search_with_bing("anything")

    assert result.startswith("Web search failed:")
    assert "timeout" in result