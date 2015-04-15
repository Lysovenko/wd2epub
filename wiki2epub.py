#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"converting file, loaded from wiki to epub"
# wd2epub (C) 2013 Serhiy Lysovenko
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from sys import argv
from index_con import get_enc_name, TabOfCont, tagstring
from os.path import join
from os import chdir, getcwd, makedirs, system
from pg_pars import HTMLDocument
from doc_glob import DocGlobals
from argparse import ArgumentParser
from hashlib import md5
from html import escape

LANGUAGE = 'en'


def get_ind_list(fname, glob):
    glob["docs"] += [fname]
    glob['IDr'] += [set()]
    glob['IDf'] += [[]]
    glob["cur_num"] += 1
    toc = TabOfCont(fname, None, glob)
    title = idstr(toc.document, "firstHeading")
    toc.dropleave()
    toc.mk_iref()
    ilst = glob['reflist']
    glob['reflist'] = []
    if ilst:
        f, r, n, l = ilst.pop(0)
    else:
        f = glob["cur_num"]
        r = -1
        l = 1
    n = title
    olst = [(f, r, n, l)]
    for f, r, n, l in ilst:
        olst.append((f, r, n, l + 1))
    return olst


def mk_epub(fnames, epub_name, title):
    iglb = DocGlobals({"any_class": {"toc"}, "cur_num": -1,
                       'dest_dir': 'OEBPS'})
    iglb['title'] = title
    iglb['author'] = 'wikipedia'
    iglb['publisher'] = 'wikipedia'
    reflist = []
    for fname in fnames:
        reflist += get_ind_list(fname, iglb)
    iglb['reflist'] = reflist
    iglb.pop("any_class")
    iglb["drop_class"] = {"portal", "toc", "mw-editsection", "mw-jump",
                          "NavToggle", "NavHead", "metadata", "infobox",
                          "vectorMenu", "catlinks", "noprint", "NavFrame",
                          "printfooter"}
    iglb["drop_id"] = {"mw-navigation", "footer"}
    iglb["class_to_tag"] = {"mw-headline": "a"}
    iglb['language'] = LANGUAGE
    if LANGUAGE.lower() != "en":
        iglb["fonts_required"] = set()
    iglb['hash'] = md5(repr(iglb).encode('utf-8')).hexdigest()
    makedirs('OEBPS')
    iglb.treat_text(None)
    if iglb.id_warns():
        return
    iglb.treat_imgs()
    iglb.make_stylesheet()
    cfn = join(iglb['data_dir'], 'core.zip')
    iglb.toc_write(join('OEBPS', 'toc.ncx'))
    iglb.opf_write(join('OEBPS', 'content.opf'))
    system('cp -f "%s" "%s"' % (cfn, epub_name))
    system('zip -X "%s" OEBPS -rq' % epub_name)
    system('rm -rf OEBPS')


def idslist(doc, theid, arr):
    global LANGUAGE
    if 'data' not in doc:
        return
    if 'attrs' in doc and 'id' in doc['attrs'] and\
            doc['attrs']['id'] == theid:
        tagstring(doc, arr)
        if 'lang' in doc['attrs']:
            LANGUAGE = doc['attrs']['lang']
        return True
    for i in doc['data']:
        if type(i) == dict:
            if idslist(i, theid, arr):
                return True


def idstr(doc, theid):
    body = None
    for i in doc['data']:
        if type(i) == dict and i['tag'] == 'body':
            body = i
            break
    if body is None:
        return
    arr = []
    idslist(body, theid, arr)
    return ''.join(arr)

if __name__ == '__main__':
    from sys import argv
    mk_epub(argv[1:-2], argv[-2], argv[-1])
