from chunking import RawGitHubDownloader, chunk_document

downloader = RawGitHubDownloader()

raw_doc = downloader.get_document("BenGale93/cli-diary/refs/heads/master/README.md")
doc = chunk_document(raw_doc, "markdown")

print(doc.get_section("cli-diary"))
