"""Document loaders for the ingestion pipeline.

Reads raw files from the knowledge source directory and converts them into
LangChain ``Document`` objects. Supported formats:

- Markdown (``.md``)
- Plain text (``.txt``)
- PDF (``.pdf``) — only when an optional parser is installed

Every document keeps a ``source`` metadata entry pointing back to the original
file (the repo-relative path), so retrieval can show where a chunk came from.

This module lives next to the existing ``aila.knowledge`` helpers and reuses
the same notion of a single ``source`` metadata key, so it is compatible with
the legacy loader without replacing it.
"""

from __future__ import annotations

import os
from pathlib import Path

from langchain_core.documents import Document


PROJECT_ROOT = Path(__file__).resolve().parents[4]


def default_knowledge_dir() -> Path:
    """Return the default raw-document directory (``knowledge/documents``)."""

    return PROJECT_ROOT / "knowledge" / "documents"


SUPPORTED_SUFFIXES = (".md", ".txt", ".pdf")


def _normalize_source(path: Path) -> str:
    """Return the repo-relative forward-slash path for a document.

    ``os.path.relpath`` is used instead of ``Path.relative_to`` so that files
    outside the project root still produce a stable, non-crashing source value.
    On Windows a file on a different drive has no relative path, so the
    absolute path is used as the fallback source.
    """

    path = path.resolve()

    try:
        rel = os.path.relpath(path, PROJECT_ROOT)
    except ValueError:
        # 跨盘符（如 C: 与 E:）时无法计算相对路径，回退为绝对路径。
        return path.as_posix()

    return Path(rel).as_posix()


def _read_pdf(path: Path) -> str:
    """Extract text from a PDF using whichever parser is installed.

    No heavy dependency is added to the project: the parser is imported
    lazily, and the caller gets a clear message when none is available.
    """

    try:
        from pypdf import PdfReader  # type: ignore[import-not-found]
    except ImportError:
        pass
    else:
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    try:
        import pdfplumber  # type: ignore[import-not-found]
    except ImportError:
        pass
    else:
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    raise RuntimeError(
        f"Cannot read PDF {path}: no PDF parser is installed. "
        "Install one (e.g. `pip install pypdf`) to enable PDF ingestion."
    )


def load_file(path: Path) -> list[Document]:
    """Load a single raw file into a one-element ``Document`` list.

    Args:
        path: Path to a ``.md``, ``.txt`` or ``.pdf`` file.

    Returns:
        A list containing one ``Document`` whose ``metadata["source"]`` is the
        repo-relative path and ``metadata["file_path"]`` the absolute path.

    Raises:
        FileNotFoundError: When ``path`` does not exist (friendly message).
        ValueError: When the file extension is not supported.
        RuntimeError: When a PDF is requested but no parser is installed.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    suffix = path.suffix.lower()

    if suffix in (".md", ".txt"):
        text = path.read_text(encoding="utf-8")
    elif suffix == ".pdf":
        text = _read_pdf(path)
    else:
        raise ValueError(
            f"Unsupported file type {suffix!r}: {path}. "
            f"Supported types: {', '.join(SUPPORTED_SUFFIXES)}"
        )

    source = _normalize_source(path)

    return [
        Document(
            page_content=text,
            metadata={
                "source": source,
                "file_path": str(path.resolve()),
            },
        )
    ]


def load_documents(directory: Path | None = None) -> list[Document]:
    """Load every supported file under ``directory`` (recursive).

    Args:
        directory: Directory to scan. Defaults to ``knowledge/documents``.

    Returns:
        A list of ``Document`` objects, in a stable (sorted) order. A missing
        directory is treated as empty rather than raising, matching the legacy
        loader.
    """

    directory = Path(directory) if directory is not None else default_knowledge_dir()

    if not directory.exists():
        return []

    documents: list[Document] = []

    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            documents.extend(load_file(path))

    return documents
