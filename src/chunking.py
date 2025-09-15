"""Let's do some dependency injection.

Say we wanted to do a bunch of documents. Creating an httpx client internally each time isn't great.
"""

import re
import typing as t

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


def chunk_document(
    document: str, doc_type: t.Literal["markdown", "latex"]
) -> list[dict[str, t.Any]]:
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

    sections = []
    current_heading = None
    current_content = []
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
                sections.append(
                    {"title": current_heading, "content": "\n".join(current_content).strip()}
                )

            current_heading = h1_match.group(1)
            current_content = []
        else:
            current_content.append(line)

    sections.append({"title": current_heading, "content": "\n".join(current_content).strip()})

    return sections
