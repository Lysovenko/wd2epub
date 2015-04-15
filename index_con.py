#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"index.html convert to toc"
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


from html.parser import HTMLParser
from sys import hexversion
from pg_pars import HTMLDocument
import os.path as osp


class EncNameParser(HTMLParser):
    def __init__(self, **di):
        if hexversion >= 0x03020000:
            di['strict'] = False
        HTMLParser.__init__(self, **di)
        self.enc_name = None

    def handle_starttag(self, tag, attrs):
        if tag.lower() != 'meta':
            return
        datrs = {}
        for nam, val in attrs:
            datrs[nam.lower()] = val
        if 'http-equiv' in datrs and 'content' in datrs:
            s = datrs['content']
            sl = s.lower()
            if 'charset' in sl:
                s = s[s.find('=', sl.find('charset')) + 1:].split(';')[0]
                self.enc_name = s.strip()


def get_enc_name(fn):
    fp = open(fn, encoding='latin1')
    text = fp.read()
    fp.close()
    if text.startswith('<?xml'):
        ep = text.find('?>')
        for i in text[6:ep].split():
            nam, val = i.split('=')
            if nam == 'encoding':
                return val[1:-1]
    parser = EncNameParser()
    parser.feed(text)
    parser.close()
    return parser.enc_name


def tagstring(doc, oarr):
    if 'data' not in doc:
        return
    for i in doc['data']:
        if type(i) == str:
            oarr.append(i)
        else:
            tagstring(i, oarr)


class TabOfCont(HTMLDocument):
    def mk_iref(self):
        if self.document is None:
            return
        body = None
        for i in self.document['data']:
            if type(i) == dict and i['tag'] == 'body':
                body = i
                break
        if body:
            self.treat_tag(body)
            prev = 0
            itms = self.globs['reflist']
            for i in range(len(itms)):
                pos, lab, nam, lr = itms[i]
                if lr == 0:
                    lr = 1
                    itms[i] = (pos, lab, nam, lr)
                if lr - prev > 1:
                    lr = prev + 1
                    itms[i] = (pos, lab, nam, lr)
                prev = lr
            self.document = None
            self._scan_reflist()

    def treat_tag(self, doc, ptags=[]):
        "recursive doc modifier"
        tag = doc['tag']
        glbs = self.globs
        if tag in {'script', 'style', 'video', 'del', 'applet', 'object',
                   'bdi', 'button', 'canvas', 'form', 'select'}:
            return
        if 'class_to_tag' in glbs and 'attrs' in doc and \
                'class' in doc['attrs']:
            for cls in doc['attrs']['class'].split():
                if cls in glbs['class_to_tag']:
                    tag = glbs['class_to_tag'][cls]
        if tag == 'a':
            if 'href' not in doc['attrs']:
                return
            if doc['attrs']['href'].startswith('http://'):
                return
            pth, ref = (tuple(doc['attrs']['href'].split('#'))
                        + (None,))[:2]
            if pth == '':
                np = glbs['docs'][glbs['cur_num']]
            else:
                np = osp.normpath(osp.join(glbs['doc_dir'], pth))
                if np not in glbs['docs']:
                    glbs['docs'].append(np)
                    glbs['IDr'].append(set())
                    glbs['IDf'].append([])
            pos = glbs['docs'].index(np)
            layer = sum([1 for i in ptags if i['tag'] in {'ul', 'ol'}])
            if ref:
                if ref not in glbs['IDs']:
                    glbs['IDs'].append(ref)
                iref = glbs['IDs'].index(ref)
            else:
                iref = -1
            name = []
            tagstring(doc, name)
            name = ''.join(name).strip()
            glbs['reflist'].append((pos, iref, name, layer))
            return
        if 'data' not in doc:
            return
        data = doc['data']
        if not data:
            return
        i = 0
        tagl = ptags + [doc]
        for i in data:
            if type(i) == dict:
                self.treat_tag(i, tagl)

    def _scan_reflist(self):
        idr = self.globs['IDr']
        for f, r, n, l in self.globs['reflist']:
            if r >= 0:
                idr[f].add(r)
