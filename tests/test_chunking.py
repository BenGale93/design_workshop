import typing as t
from unittest.mock import MagicMock

import pytest

from chunking import chunk_document, download_document_from_github


def test_no_h1_or_h2():
    document = "Hello World\n"

    doc = chunk_document(document, doc_type="markdown")

    assert doc == [{"title": None, "content": "Hello World"}]


def test_just_h1():
    document = "# Hello\n\nWorld\n"

    doc = chunk_document(document, doc_type="markdown")

    assert doc == [{"title": "Hello", "content": "World"}]


def test_starts_before_h1():
    document = "Morning\n\n# Hello\n\nWorld\n"

    doc = chunk_document(document, doc_type="markdown")

    assert doc == [
        {"title": None, "content": "Morning"},
        {"title": "Hello", "content": "World"},
    ]


def test_multi_h1():
    document = "# Hello\n\nWorld\n\n# Content\n\nHere"

    doc = chunk_document(document, doc_type="markdown")

    assert doc == [
        {"title": "Hello", "content": "World"},
        {"title": "Content", "content": "Here"},
    ]


def test_markdown_header_in_code_is_ignored_h1():
    document = "# Content\n\n```\n# Code comment\n```\n\nHere\n\n## More\n\nStuff"

    doc = chunk_document(document, doc_type="markdown")

    assert doc == [
        {"title": "Content", "content": "```\n# Code comment\n```\n\nHere\n\n## More\n\nStuff"}
    ]


def test_duplicate_h1_header():
    document = "# Hello\n\nWorld\n\n# Hello\n\nHere"
    doc = chunk_document(document, doc_type="markdown")

    assert doc == [
        {"title": "Hello", "content": "World"},
        {"title": "Hello", "content": "Here"},
    ]


def test_latex_single_section():
    document = "\\section{Hello}\n\nWorld\n\n\\subsection{Content}\n\nHere"

    doc = chunk_document(document, doc_type="latex")

    assert doc == [
        {
            "title": "Hello",
            "content": "World\n\n\\subsection{Content}\n\nHere",
        }
    ]


def test_latex_starts_blank():
    document = "Hello\n\n\\section{Hello}\n\nWorld\n\n\\subsection{Content}\n\nHere"

    doc = chunk_document(document, doc_type="latex")

    assert doc == [
        {"title": None, "content": "Hello"},
        {
            "title": "Hello",
            "content": "World\n\n\\subsection{Content}\n\nHere",
        },
    ]


def test_download_document(monkeypatch: pytest.MonkeyPatch):
    doc_text = "# Hello\n\nWorld\n"

    def fake_get(url: str) -> t.Any:  # noqa: ARG001
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = doc_text
        return mock_response

    monkeypatch.setattr("httpx.get", fake_get)
    raw_doc = download_document_from_github("test")

    assert raw_doc == doc_text
