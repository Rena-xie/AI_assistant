"""Deterministic text cleaning for the ingestion pipeline.

Only removes formatting noise:

- normalises line endings to LF,
- strips trailing whitespace on each line,
- collapses runs of blank lines into a single blank line,
- drops leading/trailing blank lines around the document.

It never rewrites, summarises, or otherwise changes the meaning of the content.
Markdown heading markers (``#``) and leading indentation (code blocks, nested
list items) are left untouched so the document structure survives cleaning.
"""

from __future__ import annotations

import re

from langchain_core.documents import Document


_BLANK_RUN = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    """Return ``text`` with whitespace noise removed and semantics intact."""

    # 1. Normalise line endings to LF.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Strip trailing whitespace per line only. Leading indentation is kept
    #    so Markdown code blocks and nested lists are not damaged.
    lines = [line.rstrip() for line in text.split("\n")]

    # 3. Collapse 3+ consecutive newlines (>=2 blank lines) into one blank line,
    #    then drop blank lines at the very start/end of the document.
    cleaned = _BLANK_RUN.sub("\n\n", "\n".join(lines)).strip("\n")

    return cleaned


def clean_documents(documents: list[Document]) -> list[Document]:
    """Clean every document's content while preserving its metadata."""

    cleaned: list[Document] = []

    for doc in documents:
        cleaned.append(
            Document(
                page_content=clean_text(doc.page_content),
                metadata=dict(doc.metadata),
            )
        )

    return cleaned
