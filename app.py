from chunking import chunk_document, download_document_from_github

raw_doc = download_document_from_github("BenGale93/cli-diary/refs/heads/master/README.md")
doc = chunk_document(raw_doc, "markdown")

section = next(s for s in doc if s["title"] == "cli-diary")

print(section)
