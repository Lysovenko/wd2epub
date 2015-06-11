# wd2epub
creates epub file from the set of html files

## Installation
Just make symbolic link on \_\_main\_\_.py

## Usage
* Download website using _swig_ or other program.
* Create the index file.
* Ctreate there the _bibinfo.txt_ file.
* Run <tt>wd2epub . destination.epub</tt>

## bibinfo.txt syntax
The _bibinfo.txt_ consists of field per line data. Field name is separated from data by column.

Possible fields:
* _title_: the title of the book
* _author_: the author of the book
* _publisher_: publisher of the book
* _drop\_class_: class to be dropped (e.g. to remove navigation bars)
* _drop\_id_: id to be removed
_language_: language of the book
* _index_ File with index (table of books contents)
* _any\_class_: required class (renome all other)
* _keep\_local\_refs_: do wat it sayed :-)
* _screen_: w h
* _fonts\_required: if embeded fonts are reqired_
* _class\_to\_tag_: (class=tag) convert some classes to tags.

