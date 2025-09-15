from chunking import RawGitHubDownloader, chunk_document

downloader = RawGitHubDownloader()

raw_doc = downloader.get_document("sphinx-doc/sphinx/refs/heads/master/doc/faq.rst")
doc = chunk_document(raw_doc, "rst")

print(doc.get_section("How do I..."))
