"""Tests for the document ingestion pipeline (load -> clean -> split).

The load/clean/split half of the pipeline is offline, so these tests use
``tmp_path`` fixtures and never touch the embedding API or a real vectorstore.
"""

from pathlib import Path

import pytest

from langchain_core.documents import Document

from aila.knowledge.ingestion.cleaner import clean_text
from aila.knowledge.ingestion.loader import load_documents, load_file
from aila.knowledge.ingestion.pipeline import build_chunks

from aila.knowledge.vectorstore import create_vectorstore


def test_markdown_loads(tmp_path):
    """1. A Markdown file is loaded into a single Document."""

    md = tmp_path / "note.md"
    md.write_text("# 标题\n\n正文内容。", encoding="utf-8")

    docs = load_file(md)

    assert len(docs) == 1
    assert docs[0].page_content == "# 标题\n\n正文内容。"


def test_txt_loads(tmp_path):
    """2. A plain-text file is loaded into a single Document."""

    txt = tmp_path / "notes.txt"
    txt.write_text("plain text\nline two", encoding="utf-8")

    docs = load_file(txt)

    assert len(docs) == 1
    assert "plain text" in docs[0].page_content
    assert "line two" in docs[0].page_content


def test_metadata_source_is_correct(tmp_path):
    """3. Loaded documents carry a non-empty, repo-relative source."""

    src = tmp_path / "doc.md"
    src.write_text("content", encoding="utf-8")

    docs = load_file(src)

    metadata = docs[0].metadata

    assert "source" in metadata
    assert metadata["source"], "source must not be empty"
    assert metadata["source"].endswith("doc.md")
    # Forward slashes on every platform (portable, matches the existing loader).
    assert "\\" not in metadata["source"]


def test_cleaner_removes_extra_whitespace():
    """4. The cleaner strips noise but preserves Markdown structure."""

    text = "  第一行  \n\n\n\n第二行\n\n\n# 标题\n\n\n内容。\n\n"

    result = clean_text(text)

    # 行尾空白被去除
    assert "第一行  \n" not in result and "第一行  " not in result
    # 连续空行折叠为单个空行
    assert "\n\n\n" not in result
    # 首尾空行被去除
    assert not result.startswith("\n") and not result.endswith("\n")
    # Markdown 标题结构保留
    assert "# 标题" in result
    # 行首缩进（代码块 / 列表）保留，语义不变
    assert "  第一行" in result
    assert "第二行" in result
    assert "内容。" in result


def test_cleaner_keeps_semantics():
    """4b. Cleaning must not rewrite content."""

    original = "## 标题\n\n- 项目一\n- 项目二\n\n    code = 1\n"
    cleaned = clean_text(original)

    assert "## 标题" in cleaned
    assert "- 项目一" in cleaned
    assert "- 项目二" in cleaned
    assert "    code = 1" in cleaned


def test_pipeline_generates_chunks(tmp_path):
    """5. The pipeline produces chunks; a long file is split."""

    md = tmp_path / "a.md"
    md.write_text("# 标题\n\n" + "知识段落内容。\n" * 500, encoding="utf-8")

    txt = tmp_path / "b.txt"
    txt.write_text("short note", encoding="utf-8")

    chunks = build_chunks(tmp_path)

    assert chunks, "pipeline should produce at least one chunk"
    assert all(isinstance(chunk, Document) for chunk in chunks)

    # 长文件被切分为多个 chunk（split 生效）
    assert len(chunks) > 1


def test_load_documents_scans_recursively(tmp_path):
    """load_documents 递归扫描并跳过不支持的文件类型。"""

    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "a.md").write_text("md content", encoding="utf-8")
    (tmp_path / "b.txt").write_text("txt content", encoding="utf-8")
    (tmp_path / "ignored.jpg").write_bytes(b"fake")

    docs = load_documents(tmp_path)

    sources = [doc.metadata["source"] for doc in docs]
    assert len(docs) == 2
    assert any(s.endswith("a.md") for s in sources)
    assert any(s.endswith("b.txt") for s in sources)


def test_missing_file_raises_friendly_error(tmp_path):
    """loader 对不存在的文件给出友好报错。"""

    missing = tmp_path / "nope.md"

    with pytest.raises(FileNotFoundError, match="not found"):
        load_file(missing)


def test_create_vectorstore_clears_old_store_before_rebuild(tmp_path, monkeypatch):
    """全量重建前必须清理旧的本地 Chroma 数据，避免新旧数据重复。"""

    store_path = tmp_path / "knowledge" / "vectorstore"
    store_path.mkdir(parents=True)
    stale_file = store_path / "chroma.sqlite3"
    stale_file.write_text("stale data", encoding="utf-8")

    # 记录 from_documents 被调用那一刻旧数据的残留情况。
    calls = {}

    class FakeChroma:
        @classmethod
        def from_documents(cls, documents, embedding, persist_directory):
            target = Path(persist_directory)
            calls["documents"] = documents
            calls["embedding"] = embedding
            calls["persist_directory"] = persist_directory
            calls["files"] = sorted(p.name for p in target.rglob("*") if p.is_file())
            return "fake-vectorstore"

    monkeypatch.setattr("aila.knowledge.vectorstore.VECTORSTORE_PATH", store_path)
    monkeypatch.setattr("aila.knowledge.vectorstore.Chroma", FakeChroma)
    monkeypatch.setattr("aila.knowledge.vectorstore.create_embeddings", lambda: "fake-embeddings")

    chunks = [Document(page_content="new chunk")]

    result = create_vectorstore(chunks)

    # 旧的 vectorstore 数据在写入前已被清理
    assert calls["files"] == []
    assert calls["persist_directory"] == str(store_path)
    assert calls["documents"] is chunks
    assert calls["embedding"] == "fake-embeddings"
    assert result == "fake-vectorstore"


def test_create_vectorstore_works_when_store_missing(tmp_path, monkeypatch):
    """旧目录不存在时，create_vectorstore 应正常创建。"""

    store_path = tmp_path / "knowledge" / "vectorstore"

    calls = {}

    class FakeChroma:
        @classmethod
        def from_documents(cls, documents, embedding, persist_directory):
            calls["persist_directory"] = persist_directory
            return "fake-vectorstore"

    monkeypatch.setattr("aila.knowledge.vectorstore.VECTORSTORE_PATH", store_path)
    monkeypatch.setattr("aila.knowledge.vectorstore.Chroma", FakeChroma)
    monkeypatch.setattr("aila.knowledge.vectorstore.create_embeddings", lambda: "fake-embeddings")

    result = create_vectorstore([Document(page_content="chunk")])

    assert not store_path.exists()
    assert calls["persist_directory"] == str(store_path)
    assert result == "fake-vectorstore"
