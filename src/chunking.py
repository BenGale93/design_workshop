"""Let us put it to the test with ReST chunking."""

import re
import typing as t
from dataclasses import dataclass, field

import httpx


class RawGitHubDownloader:
    """Downloads raw documents hosted on GitHub."""

    def __init__(
        self,
        client: httpx.Client | None = None,
        base_url: str = "https://raw.githubusercontent.com/",
    ) -> None:
        """Initialise the downloader with a client and base_url."""
        self.client = client or httpx.Client()
        self.base_url = base_url

    def get_document(self, url: str) -> str:
        """Get the text of the document at the given GitHub repo."""
        response = self.client.get(url=self.base_url + url)
        response.raise_for_status()

        return response.text


@dataclass
class Section:
    """A section of a document."""

    title: str | None
    content: str


@dataclass
class ChunkedDocument:
    """A chunked document."""

    sections: list[Section] = field(default_factory=list)

    def add_section(self, title: str | None, content: list[str]) -> None:
        """Add a section to the chunked document.

        Args:
            title: Title of the section.
            content: Content of the section.
        """
        self.sections.append(Section(title, "\n".join(content).strip()))

    def get_sections_with_title(self, title: str | None) -> list[Section]:
        """Return all sections with the given title."""
        return [section for section in self.sections if section.title == title]

    def get_section(self, title: str | None) -> Section:
        """Return a unique section.

        Args:
            title: Title of the section.

        Raises:
            ValueError: If 0 or more than 1 section has the given title
        """
        sections = self.get_sections_with_title(title)
        if (num_sections := len(sections)) != 1:
            msg = f"The title '{title}' resulted in '{num_sections}' being found."
            raise ValueError(msg)
        return sections[0]


class Chunker(t.Protocol):
    def chunk_document(self, document: str) -> ChunkedDocument: ...


class MarkdownChunker:
    h1_pattern = r"^# (.+)$"
    code_block_pattern = r"```"

    def chunk_document(self, document: str) -> ChunkedDocument:
        chunked_document = ChunkedDocument()
        current_heading: str | None = None
        current_content: list[str] = []
        in_code_block = False

        for raw_line in document.splitlines():
            line = raw_line.strip()
            if re.match(self.code_block_pattern, line):
                in_code_block = not in_code_block

            if in_code_block:
                current_content.append(line)
                continue

            h1_match = re.match(self.h1_pattern, line)

            if h1_match:
                if current_content:
                    chunked_document.add_section(current_heading, current_content)

                current_heading = h1_match.group(1)
                current_content = []
            else:
                current_content.append(line)

        chunked_document.add_section(current_heading, current_content)

        return chunked_document


class LatexChunker:
    h1_pattern = r"^\\section\{(.+)\}"

    def chunk_document(self, document: str) -> ChunkedDocument:
        chunked_document = ChunkedDocument()
        current_heading: str | None = None
        current_content: list[str] = []

        for raw_line in document.splitlines():
            line = raw_line.strip()
            h1_match = re.match(self.h1_pattern, line)
            if h1_match:
                if current_content:
                    chunked_document.add_section(current_heading, current_content)

                current_heading = h1_match.group(1)
                current_content = []
            else:
                current_content.append(line)

        chunked_document.add_section(current_heading, current_content)

        return chunked_document


class ReSTChunker:
    underline_pattern = r"^[=\-~^`#*+]+$"

    def __init__(self) -> None:
        self.level_types: list[str] = []

    def chunk_document(self, document: str) -> ChunkedDocument:
        chunked_document = ChunkedDocument()
        current_heading: str | None = None
        current_content: list[str] = []

        lines = document.splitlines()

        for i, raw_line in enumerate(lines[:-1]):
            line = raw_line.strip()
            next_line = lines[i + 1]

            if re.match(self.underline_pattern, next_line) and len(next_line) >= len(line):
                level_type = next_line[0]
                if level_type not in self.level_types:
                    # Not seen this level before
                    self.level_types.append(level_type)
                level = self.level_types.index(level_type)
                if level in {0, 1}:
                    if current_content:
                        chunked_document.add_section(current_heading, current_content)
                    current_heading = line
                    current_content = []
                else:
                    current_content.append(line)
            else:
                current_content.append(line)

        current_content.append(lines[-1])

        chunked_document.add_section(current_heading, current_content)

        return chunked_document


CHUNKERS: dict[str, Chunker] = {
    "markdown": MarkdownChunker(),
    "latex": LatexChunker(),
    "rst": ReSTChunker(),
}


def chunk_document(document: str, doc_type: str) -> ChunkedDocument:
    """Chunks a document into sections and subsections, removing any comments.

    Args:
        document: Document to chunk.
        doc_type: The type of document being chunked.

    Returns:
        Document instance containing the sections and sub-sections.
    """
    try:
        doc_chunker = CHUNKERS[doc_type]
    except KeyError:
        msg = f"{doc_type} not supported"
        raise ValueError(msg) from None

    return doc_chunker.chunk_document(document)
