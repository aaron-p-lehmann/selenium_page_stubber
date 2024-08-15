# Selenium Page Stubber

This is a utility program for creating the stubs for Selenium pages for a given
website.  It will create Page objects in modules that are implemented as
functionally as it can.  If a module already exists, it will create them as
<module>.new, so the user can copy changes as appropriate.  If you have
provided some functions in your basic Page, it will use them to crawl, if they
follow the correct interface.

# Usage

## CLI

The best CLI usage information can be found with the --help flag of the
program.

##Directory Stucture

The tool should be run from within a directory that has two directories, one
for modules for Page classes and utility functions, and one for
[jinja2](https://jinja.palletsprojects.com/en/3.1.x/) templates for building
page modules.  Their names are supplied at the command line, and default to
```pages``` and ```templates```, respectively.  There will be one module that
holds the base class for all page classes a tamplate for building a page class,
which can be componentized, if necessary.  There will be one page class called
Page.  This is the class that is the parent to every Page stuff.  Any page can
be modified manually after creation.

Here is an example directory structure:

*Main selenium project*
|
|
|
|
|
|-------> pages/
|       |
|       |
|       |-------> Page.py
|       |
|       |
|       |-------> <any number of other Page modules, one for each page>
|
|
|-------> templates/
        |
        |
        |-------> Page.jinja <template used to build pages>
        |
        |
        |-------> <any number of other templates, which can be used by Page.jinja
        
#Development

##Submitting

Before submitting any PRs, please make sure that your changes will pass the
manifest/lex/type/test checking by running:

```
tox -e testing
```

##Directory structure

This project has two directories at the main level, ```user``` and
```client```.  The modules in ```client``` might use modules and tempates from
```user```, but never vice versa.  Modules and templates in ```user``` might
be copied into the user's directories, and the users might not have this
program installed on their machines.

TODO
====
Features
--------
- CLI
- Dockerfile (headless usage)
- Everything else :)
