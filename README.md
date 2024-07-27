Selenium Page Stubber
=====================
This is a utility program for creating the stubs for Selenium pages for
a given website.  It can do this one page at a time, or you can provide
the name of a module and starting Page, and it will scrape as much as
it can, creating Page objects in files that are implemented as
functionally as it can.  If you have provided some functions in your
basic Page, it will use them to crawl, if they follow the correct
interface.

Usage
=====
The best CLI usage information can be found with the --help flag of the
program.

Development
===========
Before submitting any PRs, please make sure that your changes will pass the manifest/lex/type/test checking by running:
```
tox -e testing
```

TODO
====
Features
--------
- CLI
- Dockerfile (headless usage)
- Everything else :)
