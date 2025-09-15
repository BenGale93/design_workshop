"""Now let's make our return object more useful."""

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


def chunk_document(document: str, doc_type: t.Literal["markdown", "latex"]) -> ChunkedDocument:
    """Chunks a document into sections and subsections, removing any comments.

    Args:
        document: Document to chunk.
        doc_type: The type of document being chunked.

    Returns:
        Document instance containing the sections and sub-sections.
    """
    if doc_type == "markdown":
        h1_pattern = r"^# (.+)$"
        code_block_pattern = r"```"
    else:
        h1_pattern = r"^\\section\{(.+)\}"
        code_block_pattern = None

    chunked_document = ChunkedDocument()
    current_heading: str | None = None
    current_content: list[str] = []
    in_code_block = False

    for raw_line in document.splitlines():
        line = raw_line.strip()
        if code_block_pattern and re.match(code_block_pattern, line):
            in_code_block = not in_code_block

        if in_code_block:
            current_content.append(line)
            continue

        h1_match = re.match(h1_pattern, line)

        if h1_match:
            if current_content:
                chunked_document.add_section(current_heading, current_content)

            current_heading = h1_match.group(1)
            current_content = []
        else:
            current_content.append(line)

    chunked_document.add_section(current_heading, current_content)

    return chunked_document
