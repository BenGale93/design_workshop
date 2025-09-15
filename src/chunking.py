"""Initial example."""

import re
import typing as t

import httpx


def download_document_from_github(url: str) -> str:
    """Download the raw contents of a document from a GitHub repo."""
    base_url = "https://raw.githubusercontent.com/"
    response = httpx.get(url=base_url + url)
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
