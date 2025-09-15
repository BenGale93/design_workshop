import typing as t
from http import HTTPStatus

import httpx
import pytest

from chunking import ChunkedDocument, RawGitHubDownloader, Section, chunk_document


def test_no_h1_or_h2():
    document = "Hello World\n"

    doc = chunk_document(document, doc_type="markdown")

    assert doc == ChunkedDocument(sections=[Section(title=None, content="Hello World")])


def test_just_h1():
    document = "# Hello\n\nWorld\n"

    doc = chunk_document(document, doc_type="markdown")

    assert doc == ChunkedDocument(sections=[Section(title="Hello", content="World")])


def test_starts_before_h1():
    document = "Morning\n\n# Hello\n\nWorld\n"

    doc = chunk_document(document, doc_type="markdown")

    assert doc == ChunkedDocument(
        sections=[
            Section(title=None, content="Morning"),
            Section(title="Hello", content="World"),
        ]
    )


def test_multi_h1():
    document = "# Hello\n\nWorld\n\n# Content\n\nHere"

    doc = chunk_document(document, doc_type="markdown")

    assert doc == ChunkedDocument(
        sections=[
            Section(title="Hello", content="World"),
            Section(title="Content", content="Here"),
        ]
    )


def test_markdown_header_in_code_is_ignored_h1():
    document = "# Content\n\n```\n# Code comment\n```\n\nHere\n\n## More\n\nStuff"

    doc = chunk_document(document, doc_type="markdown")

    assert doc == ChunkedDocument(
        sections=[
            Section(title="Content", content="```\n# Code comment\n```\n\nHere\n\n## More\n\nStuff")
        ]
    )


def test_duplicate_h1_header():
    document = "# Hello\n\nWorld\n\n# Hello\n\nHere"
    doc = chunk_document(document, doc_type="markdown")

    assert doc == ChunkedDocument(
        sections=[
            Section(title="Hello", content="World"),
            Section(title="Hello", content="Here"),
        ]
    )


def test_latex_single_section():
    document = "\\section{Hello}\n\nWorld\n\n\\subsection{Content}\n\nHere"

    doc = chunk_document(document, doc_type="latex")

    assert doc == ChunkedDocument(
        sections=[
            Section(
                title="Hello",
                content="World\n\n\\subsection{Content}\n\nHere",
            ),
        ]
    )


def test_latex_starts_blank():
    document = "Hello\n\n\\section{Hello}\n\nWorld\n\n\\subsection{Content}\n\nHere"

    doc = chunk_document(document, doc_type="latex")

    assert doc == ChunkedDocument(
        sections=[
            Section(
                title=None,
                content="Hello",
            ),
            Section(
                title="Hello",
                content="World\n\n\\subsection{Content}\n\nHere",
            ),
        ]
    )


def test_bad_doc_type():
    with pytest.raises(ValueError, match="fake not supported"):
        chunk_document("", "fake")


@pytest.fixture
def get_downloader() -> t.Callable[[str], RawGitHubDownloader]:
    def _create_client(content: str) -> RawGitHubDownloader:
        test_client = httpx.Client(
            transport=httpx.MockTransport(lambda _: httpx.Response(HTTPStatus.OK, content=content))
        )
        return RawGitHubDownloader(client=test_client)

    return _create_client


def test_download_document(get_downloader):
    doc_text = "# Hello\n\nWorld\n"

    downloader = get_downloader(doc_text)

    raw_doc = downloader.get_document("test")

    assert raw_doc == doc_text


class TestChunkedDocument:
    def test_get_h1_unique(self):
        doc = ChunkedDocument([Section(None, "1"), Section("Test", "2")])

        assert doc.get_section("Test").content == "2"

    def test_get_h1_not_found(self):
        doc = ChunkedDocument([Section(None, "1"), Section("Test", "2")])

        with pytest.raises(ValueError, match="resulted in '0'"):
            doc.get_section("Fake")

    def test_get_h1_too_many(self):
        doc = ChunkedDocument([Section("Test", "1"), Section("Test", "2")])

        with pytest.raises(ValueError, match="resulted in '2'"):
            doc.get_section("Test")
