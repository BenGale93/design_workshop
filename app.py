from chunking import RawGitHubDownloader, chunk_document

downloader = RawGitHubDownloader()

raw_doc = downloader.get_document("BenGale93/cli-diary/refs/heads/master/README.md")
doc = chunk_document(raw_doc, "markdown")

section = next(s for s in doc if s["title"] == "cli-diary")

print(section)
