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

TODO
====
Setup Stuff
-----------
- pip package file
- write toml file

Features
--------
- CLI
- Dockerfile (headless usage)
- Everything else :)

Getting Started Locally with Dockerized Container 
=================================================
Prerequisite
--------
- Docker
  
Pull the repository
-------------------
```
git clone https://github.com/iamkashifyousuf/selenium_page_stubber.git 
```
Building Image
--------------
```
docker build -t selenium_page_stubber:latest .
```
Run the Docker Container & Pass Arguments to the CLI
----------------------------------------------------
```
docker run -it selenium_page_stubber:latest <your-arguments-here>
```
Example
------
```
docker run -it selenium_page_stubber:latest --help
```

HELP
----
Usage: cli.py [OPTIONS] SITE

  Stub out Page classes for each page in SITE.

Options:
  --page-directory PATH      The path to the directory where the Page modules
                             are
  --page-class TEXT          The name of the base Page class
  --template-directory PATH  The path to the Jinja apps for building the
                             pages.
  --output-directory PATH    The directory to put the Pages into
  --page-module TEXT         The module the base page class is in
  --help                     Show this message and exit.



  
