#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"parse html page"
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


# http://www.w3schools.com/tags/
from html.parser import HTMLParser
from html import escape
from sys import hexversion
from os import popen
import os.path as osp

# html character entity feferences got from
# http://en.wikipedia.org/wiki/List_of_XML_and_HTML_character_entity_references
SPEC_ENTS = {"quot": "\u0022", "apos": "\u0027", "nbsp": "\u00A0",
             "iexcl": "\u00A1", "cent": "\u00A2", "pound": "\u00A3",
             "curren": "\u00A4", "yen": "\u00A5", "brvbar": "\u00A6",
             "sect": "\u00A7", "uml": "\u00A8", "copy": "\u00A9",
             "ordf": "\u00AA", "laquo": "\u00AB", "not": "\u00AC",
             "shy": "\u00AD", "reg": "\u00AE", "macr": "\u00AF",
             "deg": "\u00B0", "plusmn": "\u00B1", "sup2": "\u00B2",
             "sup3": "\u00B3", "acute": "\u00B4", "micro": "\u00B5",
             "para": "\u00B6", "middot": "\u00B7", "cedil": "\u00B8",
             "sup1": "\u00B9", "ordm": "\u00BA", "raquo": "\u00BB",
             "frac14": "\u00BC", "frac12": "\u00BD", "frac34": "\u00BE",
             "iquest": "\u00BF", "Agrave": "\u00C0", "Aacute": "\u00C1",
             "Acirc": "\u00C2", "Atilde": "\u00C3", "Auml": "\u00C4",
             "Aring": "\u00C5", "AElig": "\u00C6", "Ccedil": "\u00C7",
             "Egrave": "\u00C8", "Eacute": "\u00C9", "Ecirc": "\u00CA",
             "Euml": "\u00CB", "Igrave": "\u00CC", "Iacute": "\u00CD",
             "Icirc": "\u00CE", "Iuml": "\u00CF", "ETH": "\u00D0",
             "Ntilde": "\u00D1", "Ograve": "\u00D2", "Oacute": "\u00D3",
             "Ocirc": "\u00D4", "Otilde": "\u00D5", "Ouml": "\u00D6",
             "times": "\u00D7", "Oslash": "\u00D8", "Ugrave": "\u00D9",
             "Uacute": "\u00DA", "Ucirc": "\u00DB", "Uuml": "\u00DC",
             "Yacute": "\u00DD", "THORN": "\u00DE", "szlig": "\u00DF",
             "agrave": "\u00E0", "aacute": "\u00E1", "acirc": "\u00E2",
             "atilde": "\u00E3", "auml": "\u00E4", "aring": "\u00E5",
             "aelig": "\u00E6", "ccedil": "\u00E7", "egrave": "\u00E8",
             "eacute": "\u00E9", "ecirc": "\u00EA", "euml": "\u00EB",
             "igrave": "\u00EC", "iacute": "\u00ED", "icirc": "\u00EE",
             "iuml": "\u00EF", "eth": "\u00F0", "ntilde": "\u00F1",
             "ograve": "\u00F2", "oacute": "\u00F3", "ocirc": "\u00F4",
             "otilde": "\u00F5", "ouml": "\u00F6", "divide": "\u00F7",
             "oslash": "\u00F8", "ugrave": "\u00F9", "uacute": "\u00FA",
             "ucirc": "\u00FB", "uuml": "\u00FC", "yacute": "\u00FD",
             "thorn": "\u00FE", "yuml": "\u00FF", "OElig": "\u0152",
             "oelig": "\u0153", "Scaron": "\u0160", "scaron": "\u0161",
             "Yuml": "\u0178", "fnof": "\u0192", "circ": "\u02C6",
             "tilde": "\u02DC", "Alpha": "\u0391", "Beta": "\u0392",
             "Gamma": "\u0393", "Delta": "\u0394", "Epsilon": "\u0395",
             "Zeta": "\u0396", "Eta": "\u0397", "Theta": "\u0398",
             "Iota": "\u0399", "Kappa": "\u039A", "Lambda": "\u039B",
             "Mu": "\u039C", "Nu": "\u039D", "Xi": "\u039E",
             "Omicron": "\u039F", "Pi": "\u03A0", "Rho": "\u03A1",
             "Sigma": "\u03A3", "Tau": "\u03A4", "Upsilon": "\u03A5",
             "Phi": "\u03A6", "Chi": "\u03A7", "Psi": "\u03A8",
             "Omega": "\u03A9", "alpha": "\u03B1", "beta": "\u03B2",
             "gamma": "\u03B3", "delta": "\u03B4", "epsilon": "\u03B5",
             "zeta": "\u03B6", "eta": "\u03B7", "theta": "\u03B8",
             "iota": "\u03B9", "kappa": "\u03BA", "lambda": "\u03BB",
             "mu": "\u03BC", "nu": "\u03BD", "xi": "\u03BE",
             "omicron": "\u03BF", "pi": "\u03C0", "rho": "\u03C1",
             "sigmaf": "\u03C2", "sigma": "\u03C3", "tau": "\u03C4",
             "upsilon": "\u03C5", "phi": "\u03C6", "chi": "\u03C7",
             "psi": "\u03C8", "omega": "\u03C9", "thetasym": "\u03D1",
             "upsih": "\u03D2", "piv": "\u03D6", "ensp": "\u2002",
             "emsp": "\u2003", "thinsp": "\u2009", "zwnj": "\u200C",
             "zwj": "\u200D", "lrm": "\u200E", "rlm": "\u200F",
             "ndash": "\u2013", "mdash": "\u2014", "lsquo": "\u2018",
             "rsquo": "\u2019", "sbquo": "\u201A", "ldquo": "\u201C",
             "rdquo": "\u201D", "bdquo": "\u201E", "dagger": "\u2020",
             "Dagger": "\u2021", "bull": "\u2022", "hellip": "\u2026",
             "permil": "\u2030", "prime": "\u2032", "Prime": "\u2033",
             "lsaquo": "\u2039", "rsaquo": "\u203A", "oline": "\u203E",
             "frasl": "\u2044", "euro": "\u20AC", "image": "\u2111",
             "weierp": "\u2118", "real": "\u211C", "trade": "\u2122",
             "alefsym": "\u2135", "larr": "\u2190", "uarr": "\u2191",
             "rarr": "\u2192", "darr": "\u2193", "harr": "\u2194",
             "crarr": "\u21B5", "lArr": "\u21D0", "uArr": "\u21D1",
             "rArr": "\u21D2", "dArr": "\u21D3", "hArr": "\u21D4",
             "forall": "\u2200", "part": "\u2202", "exist": "\u2203",
             "empty": "\u2205", "nabla": "\u2207", "isin": "\u2208",
             "notin": "\u2209", "ni": "\u220B", "prod": "\u220F",
             "sum": "\u2211", "minus": "\u2212", "lowast": "\u2217",
             "radic": "\u221A", "prop": "\u221D", "infin": "\u221E",
             "ang": "\u2220", "and": "\u2227", "or": "\u2228",
             "cap": "\u2229", "cup": "\u222A", "int": "\u222B",
             "there4": "\u2234", "sim": "\u223C", "cong": "\u2245",
             "asymp": "\u2248", "ne": "\u2260", "equiv": "\u2261",
             "le": "\u2264", "ge": "\u2265", "sub": "\u2282", "sup": "\u2283",
             "nsub": "\u2284", "sube": "\u2286", "supe": "\u2287",
             "oplus": "\u2295", "otimes": "\u2297", "perp": "\u22A5",
             "sdot": "\u22C5", "vellip": "\u22EE", "lceil": "\u2308",
             "rceil": "\u2309", "lfloor": "\u230A", "rfloor": "\u230B",
             "lang": "\u2329", "rang": "\u232A", "loz": "\u25CA",
             "spades": "\u2660", "clubs": "\u2663", "hearts": "\u2665",
             "diams": "\u2666"}


class DocHTMLParser(HTMLParser):
    "parses jusginal html file"
    def __init__(self, data, fname=None):
        di = {}
        if hexversion >= 0x030200f0:
            di['strict'] = False
        HTMLParser.__init__(self, **di)
        self.document = {'tag': 'html', 'data': []}
        self.links_to = [self.document]
        self.fmtags = []
        self.fname = fname
        self.feed(data)
        self.close()

    def warn_me(self):
        "warnings generator"
        lnks = self.links_to
        if len(lnks) < 2:
            return
        ct = lnks[-1]['tag']
        pt = lnks[-2]['tag']
        if ct in {'td', 'tr'}:
            if pt == {'td': 'tr', 'tr': 'table'}[ct]:
                return
        elif ct == 'li':
            if pt in {'ul', 'ol'}:
                return
        else:
            return
        print('%s:%d:%d:  %s in %s' % ((self.fname,) + self.getpos() +
                                       (ct, pt)))

    def handle_starttag(self, tag, attrs):
        "# print('start>>>',tag)"
        lnks = self.links_to
        if not lnks:
            print('\x1b[1;33mWarning:\x1b[0m halt at %d:%d' % self.getpos())
            return
        dattrs = dict(attrs)
        if tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'ul', 'ol',
                   'pre', 'td', 'tr', 'blockquote',
                   'dir', 'dl', 'form', 'table', 'title', 'hr', 'p', 'li'}:
            #
            if tag != 'hr':
                offtags = [i[0] for i in self.fmtags]
                offtags.reverse()
            else:
                offtags = []
            for i in offtags:
                if lnks and lnks[-1]['tag'] == i:
                    lnks.pop(-1)
            if 'p' in [i['tag'] for i in lnks]:
                while lnks[-1]['tag'] != 'p':
                    lnks.pop(-1)
            if lnks[-1]['tag'] == 'p':
                lnks.pop(-1)
        if tag in {'tr', 'dt', 'dd'}:
            while lnks[-1]['tag'] in {'td', 'th', 'dt', 'dd', 'p'}:
                lnks.pop(-1)
        if tag in {'p', 'li', 'td', 'tr', 'th'}:
            if lnks[-1]['tag'] == tag:
                lnks.pop(-1)
            poss = {'li': {'ul', 'ol', 'dir'}, 'td': {'tr'}, 'tr': {'table'}}
            if tag in poss and lnks[-1]['tag'] not in poss[tag]:
                ptgs = [i['tag'] for i in lnks]
                if any([i in ptgs for i in poss[tag]]):
                    while lnks[-1]['tag'] not in poss[tag]:
                        lnks.pop(-1)
            lnks[-1]['data'].append({'attrs': dattrs, 'tag': tag, 'data': []})
            lnks.append(lnks[-1]['data'][-1])
            if tag != 'tr':
                for tg, att in self.fmtags:
                    lnks[-1]['data'].append({'attrs': att, 'tag': tg,
                                             'data': []})
                    lnks.append(lnks[-1]['data'][-1])
            return self.warn_me()
        if tag in {'b', 'tt', 'em', 'i', 'font', 'strong',
                   'span'}:
            self.fmtags.append((tag, dattrs))
            lnks[-1]['data'].append({'attrs': dattrs, 'tag': tag, 'data': []})
            lnks.append(lnks[-1]['data'][-1])
            return self.warn_me()

        if tag in {'abbr', 'a', 'sup', 'sub', 'del', 'address',
                   'script', 'style', 'video', 'applet', 'object', 'canvas',
                   'bdi', 'dt', 'dd', 'big', 'blockquote', 'button', 'code',
                   'caption', 'center', 'cite', 'select', 'head', 'ul', 'ol',
                   'body', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div',
                   'pre', 'dir', 'dl', 'form', 'table', 'title'}:
            lnks[-1]['data'].append({'attrs': dattrs, 'tag': tag, 'data': []})
            lnks.append(lnks[-1]['data'][-1])
            return self.warn_me()
        if tag in {'img', 'br', 'hr', 'meta'}:
            lnks[-1]['data'].append({'attrs': dattrs, 'tag': tag})
            return self.warn_me()

    def handle_endtag(self, tag):
        "# print('end>', tag)"
        lnks = self.links_to
        # "I don't care" closing politics
        if tag in [i['tag'] for i in lnks]:
            while lnks[-1]['tag'] != tag:
                lnks.pop(-1)
            lnks.pop(-1)
        fmt = [i[0] for i in self.fmtags]
        if tag in fmt:
            fmt.reverse()
            self.fmtags.pop(len(fmt) - 1 - fmt.index(tag))

    def handle_data(self, data):
        if self.links_to and 'data' in self.links_to[-1]:
            self.links_to[-1]['data'].append(data)

    def handle_charref(self, name):
        if self.links_to and 'data' in self.links_to[-1]:
            symb = chr(int(name))
            if symb in '<>&':
                self.links_to[-1]['data'].append('&#%s;' % name)
            else:
                self.links_to[-1]['data'].append(symb)

    def handle_entityref(self, name):
        if self.links_to and 'data' in self.links_to[-1]:
            if name in SPEC_ENTS:
                self.links_to[-1]['data'].append(SPEC_ENTS[name])
            else:
                self.links_to[-1]['data'].append('&%s;' % name)


def write_tags(revd, fout):
    "write tagtree to file"
    showtag = 'hidden' not in revd
    if showtag:
        fout.write('<%s' % revd['tag'])
        if 'attrs' in revd and revd['attrs']:
            for i in revd['attrs']:
                if revd['attrs'][i] is None:
                    continue
                fout.write(' %s="%s"' % (i, escape(revd['attrs'][i])))
    if 'data' in revd:
        if showtag:
            fout.write('>')
        for i in revd['data']:
            if type(i) == str:
                fout.write(i)
            else:
                write_tags(i, fout)
        if showtag:
            fout.write('</%s>' % revd['tag'])
    else:
        fout.write('/>')


def treat_img_tag(doc, glbs):
    if 'src' not in doc['attrs']:
        return True
    src = doc['attrs']['src']
    if 'alt' not in doc['attrs']:
        doc['attrs']['alt'] = src
    # TODO: better to be replaced by some librarian function
    if '%' in src:
        try:
            src = eval("b'" + src.replace("%", "\\x") + "'").decode()
        except (ValueError, UnicodeDecodeError):
            pass
    # END TODO
    np = osp.normpath(osp.join(glbs['doc_dir'], src))
    if not osp.isfile(np):
        return True
    if np not in glbs['imgs']:
        glbs['imgs'].append(np)
    doc['attrs']['src'] = '../Images/i_%d.png' % glbs['imgs'].index(np)
    if 'width' in doc['attrs'] and 'height' in doc['attrs'] \
            and 'screen' not in glbs:
        w, h = float(doc['attrs']['width']), float(doc['attrs']['height'])
    else:
        with popen('identify -format "%%w %%h" "%s"' % np) as ifp:
            try:
                w, h = tuple(map(float, ifp.read().split()))
            except:
                osp.os.system('identify "%s"' % np)
                return True
    scalf = 1.0
    if 'screen' in glbs:
        sw, sh = glbs['screen']
        if max(w, h) > max(sw, sh) or min(w, h) > min(sw, sh):
            scalf = min(max(sw, sh) / max(w, h), min(sw, sh) / min(w, h))
    w = int(w * scalf + .5)
    h = int(h * scalf + .5)
    if len(glbs['imgs']) > len(glbs['img_szs']):
        if scalf < 1.0:
            glbs['img_szs'].append((w, h))
        else:
            glbs['img_szs'].append(None)
    doc['attrs']['width'] = str(w)
    doc['attrs']['height'] = str(h)
    for i in list(doc['attrs']):
        if i not in {'src', 'alt', 'width', 'height', 'id'}:
            doc['attrs'].pop(i)
    return False


def treat_table_tag(doc, glbs, ptags):
    m_cols = 0
    rows = 0
    has_caption = False
    has_th = False
    for i in doc['data']:
        if type(i) == dict:
            if i['tag'] == 'caption':
                has_caption = True
            if i['tag'] == 'tr':
                rows += 1
                cols = 0
            else:
                continue
            j = 0
            data = i['data']
            while j < len(data):
                dtj = data[j]
                if type(dtj) == dict and dtj['tag'] in {'td', 'th'}:
                    if treat_tag(dtj, glbs, ptags):
                        data.pop(j)
                        continue
                    cols += 1
                    for atr in list(dtj['attrs']):
                        if atr not in {'align', 'valign', 'colspan',
                                       'rowspan', 'id'}:
                            dtj['attrs'].pop(atr)
                        if atr in {'align', 'valign'}:
                            dtj['attrs'][i] = dtj['attrs'][i].lower()
                    if dtj['tag'] == 'th':
                        has_th = True
                else:
                    data.pop(j)
                    j -= 1
                j += 1
            if cols > m_cols:
                m_cols = cols
    if m_cols == 0:
        return True
    if not (m_cols > 1 or has_caption or has_th):
        doc['hidden'] = True
        for i in doc['data']:
            if type(i) == dict and i['tag'] == 'tr':
                i['hidden'] = True
                for j in i['data']:
                    if type(j) == dict and j['tag'] == 'td':
                        j['tag'] = 'div'
    for i in list(doc['attrs']):
        if i not in {'id', 'title', 'width'}:
            doc['attrs'].pop(i)
    return False


_symb_map = {97: '\u03b1', 98: '\u03b2', 99: '\u03c7', 100: '\u03b4',
             101: '\u03b5', 102: '\u03d5', 103: '\u03b3', 104: '\u03b7',
             105: '\u03b9', 106: '\u03c6', 107: '\u03ba', 108: '\u03bb',
             109: '\u03bc', 110: '\u03bd', 111: '\u03bf', 112: '\u03c0',
             113: '\u03b8', 114: '\u03c1', 115: '\u03c3', 116: '\u03c4',
             117: '\u03c5', 118: '\u03d6', 119: '\u03c9', 120: '\u03be',
             121: '\u03c8', 122: '\u03b6', 65: '\u0391', 66: '\u0392',
             67: '\u03a7', 68: '\u0394', 69: '\u0395', 70: '\u03a6',
             71: '\u0393', 72: '\u0397', 73: '\u0399', 74: '\u03d1',
             75: '\u039a', 76: '\u039b', 77: '\u039c', 78: '\u039d',
             79: '\u039f', 80: '\u03a0', 81: '\u0398', 82: '\u03a1',
             83: '\u03a3', 84: '\u03a4', 85: '\u03a5', 86: '\u03db',
             87: '\u03a9', 88: '\u039e', 89: '\u03a8', 90: '\u0396'}


def mk_symbol(doc):
    "convert data strings according 'Symbol' font"
    if 'data' not in doc:
        return
    data = doc['data']
    for i in range(len(data)):
        if type(data[i]) == str:
            if data[i][0] != '&' or data[i][-1] != ';' or \
                    len(data[i]) > 15 or len(data[i].split()) > 1:
                data[i] = data[i].translate(_symb_map)
        else:
            mk_symbol(data[i])


_tag_alias = {'strong': 'b', 'dir': 'ul'}


def treat_tag(doc, glbs, ptags=[]):
    "recursive doc modifier"
    tag = doc['tag']
    if tag in {'script', 'style', 'video', 'del', 'applet', 'object',
               'bdi', 'button', 'canvas', 'form', 'select'}:
        return True
    if 'class_to_tag' in glbs and 'attrs' in doc and \
            'class' in doc['attrs']:
        for cls in doc['attrs']['class'].split():
            if cls in glbs['class_to_tag']:
                tag = glbs['class_to_tag'][cls]
                doc['tag'] = tag
    if tag in _tag_alias:
        tag = _tag_alias[tag]
        doc['tag'] = tag
    if tag == 'abbr':
        nt = {'tag': "b", 'data': doc['data']}
        tag = 'i'
        doc['tag'] = tag
        if 'attrs' in doc and 'title' in doc['attrs']:
            doc['data'] = [nt, ' (', escape(doc['attrs'].pop('title')),
                           ')']
    if tag == 'a':
        if 'href' in doc['attrs']:
            if not doc['attrs']['href'].startswith('http://'):
                pth, ref = (tuple(doc['attrs']['href'].split('#'))
                            + (None,))[:2]
                if pth == '':
                    np = glbs['docs'][glbs['cur_num']]
                else:
                    np = osp.normpath(osp.join(glbs['doc_dir'], pth))
                if np not in glbs['docs']:
                    print('\x1b[1;33mWARNING:\x1b[0m unknown local file: "%s"'
                          % np)
                    if 'keep_local_refs' in glbs:
                        doc['hidden'] = True
                        np = glbs['docs'][0]
                    else:
                        return True
                pos = glbs['docs'].index(np)
                if ref:
                    if ref not in glbs['IDs']:
                        glbs['IDs'].append(ref)
                    iref = glbs['IDs'].index(ref)
                    glbs['IDr'][pos].add(iref)
                    doc['attrs']['href'] = \
                        'ht_%d.xhtml#x%x' % (pos, iref)
                elif 'keep_local_refs' in glbs:
                    doc['attrs']['href'] = 'ht_%d.xhtml' % pos
                else:
                    return True
        else:
            doc['hidden'] = True
            # let id will flow up if <a> is hidden
            if 'id' in doc['attrs'] and 'name' not in doc['attrs']:
                doc['attrs']['name'] = doc['attrs'].pop('id')
        # solving <a name=*> trouble made by Micro$oft
        if 'name' in doc['attrs']:
            tag_pos = None
            for i in range(len(ptags) - 1, -1, -1):
                if 'attrs' in ptags[i] and 'hidden' not in ptags[i]:
                    if 'id' not in ptags[i]['attrs']:
                        tag_pos = i
                        break
                    if ptags[i]['attrs']['id'] == doc['attrs']['name']:
                        break
            if tag_pos is not None:
                ptags[tag_pos]['attrs']['id'] = doc['attrs']['name']
                if 'id' in doc['attrs'] and \
                        ptags[tag_pos]['attrs']['id'] == doc['attrs']['id']:
                    doc['attrs'].pop('id')
        for i in list(doc['attrs']):
            if i not in {'href', 'id', 'title'}:
                doc['attrs'].pop(i)
    elif tag == 'img':
        return treat_img_tag(doc, glbs)
    elif tag in {'font', 'span'}:
        doc['hidden'] = True
        if 'face' in doc['attrs'] and doc['attrs']['face'].lower() == 'symbol':
            mk_symbol(doc)
    elif tag == 'table':
        return treat_table_tag(doc, glbs, ptags)
    elif tag == 'li':
        if ptags[-1]['tag'] not in {'ul', 'ol'}:
            tag = 'p'
            doc['tag'] = tag
    elif 'attrs' in doc:
        for i in list(doc['attrs']):
            if i not in {'id', 'title'}:
                doc['attrs'].pop(i)
    if tag in {'p', 'b'}:
        if ptags and ptags[-1]['tag'] in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            doc['hidden'] = True
            if 'id' in doc['attrs']:
                tag_pos = None
                for i in range(len(ptags) - 1, -1, -1):
                    if 'attrs' in ptags[i] and \
                            'id' not in ptags[i]['attrs'] and \
                            'hidden' not in ptags[i]:
                        tag_pos = i
                        break
                if tag_pos is not None:
                    ptags[tag_pos]['attrs']['id'] = doc['attrs']['id']
    if tag in {'p', 'i'}:
        if ptags and ptags[-1]['tag'] == 'blockquote':
            doc['hidden'] = True
    if 'data' not in doc:
        return False
    data = doc['data']
    if not data:
        return True
    i = 0
    tagl = ptags + [doc]
    all_ascii = True
    is_fntsr = 'fonts_required' in glbs
    space = True
    fmtag = tag in {'b', 'tt', 'em', 'i', 'font', 'span', 'blockquote'}
    while i < len(data):
        if type(data[i]) == str:
            if not data[i].isspace():
                space = False
                if data[i][0] != '&' or data[i][-1] != ';' or \
                        len(data[i]) > 15 or len(data[i].split()) > 1:
                    data[i] = escape(data[i], False)
                    if is_fntsr and all_ascii and \
                            max([ord(i) for i in data[i]]) > 127:
                        all_ascii = False
            i += 1
        else:
            if treat_tag(data[i], glbs, tagl):
                data.pop(i)
            else:
                if data[i]['tag'] != 'br' and 'ignore_me' not in data[i]:
                    space = False
                i += 1
    if fmtag and space:
        doc['ignore_me'] = True
        if tag != 'tt':
            doc['hidden'] = True
    if is_fntsr and not space and not all_ascii:
        cfp = list('rnn')
        tagl = set([i['tag'] for i in tagl])
        for i in ('b', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            if i in tagl:
                cfp[1] = 'b'
                break
        if 'i' in tagl or 'em' in tagl or 'blockquote' in tagl:
            cfp[2] = 'i'
        if 'pre' in tagl or 'tt' in tagl or 'code' in tagl:
            cfp[0] = 'm'
        cfp = ''.join(cfp)
        glbs['fonts_required'].add(cfp)
    return not fmtag and space


def treat_ids(doc, idl, idf):
    "id converter"
    if 'hidden' not in doc and 'attrs' in doc and 'id' in doc['attrs']:
        tid = doc['attrs']['id']
        if tid not in idl:
            idl.append(tid)
        iid = idl.index(tid)
        doc['attrs']['id'] = 'x%x' % iid
        idf.append(iid)
    if 'data' not in doc:
        return
    for i in doc['data']:
        if type(i) == dict:
            treat_ids(i, idl, idf)


def any_id_cls_leave(doc, cll, idl):
    "data remover"
    if cll and 'attrs' in doc and \
            'class' in doc['attrs'] and \
            ':' not in doc['attrs']['class']:
        for cls in doc['attrs']['class'].split():
            if cls in cll:
                return False
    if idl and 'attrs' in doc and \
            'id' in doc['attrs'] and \
            doc['attrs']['id'] in idl:
        return False
    if 'data' not in doc:
        return True
    data = doc['data']
    i = 0
    rv = True
    while i < len(data):
        if type(data[i]) == str or any_id_cls_leave(data[i], cll, idl):
            data.pop(i)
        else:
            i += 1
            rv = False
    return rv


def id_cls_drop(doc, cld, idd):
    if cld and 'attrs' in doc and \
            'class' in doc['attrs']:
        for cls in doc['attrs']['class'].split():
            if cls in cld:
                return True
    if idd and 'attrs' in doc and \
            'id' in doc['attrs'] and \
            doc['attrs']['id'] in idd:
        return True
    if 'data' not in doc:
        return False
    data = doc['data']
    if not data:
        return False
    i = 0
    rv = True
    while i < len(data):
        if type(data[i]) == dict and id_cls_drop(data[i], cld, idd):
            data.pop(i)
        else:
            i += 1
            rv = False
    return rv


def space_drop(doc):
    if not (doc['tag'] == 'div' or 'hidden' in doc):
        return True
    drp_spc = True
    i = 0
    data = doc['data']
    divonly = True
    while i < len(data):
        if type(data[i]) == str:
            if drp_spc and data[i].isspace():
                data.pop(i)
                continue
            drp_spc = False
        elif space_drop(data[i]):
            divonly = False
        i += 1
    if drp_spc and divonly and not doc.get('attrs'):
        doc['hidden'] = True


class HTMLDocument:
    def __init__(self, fname, coding, globs):
        self.document = None
        self.filename = fname
        self.globs = globs
        if fname is None:
            return
        with open(fname, encoding=coding) as fptr:
            data = fptr.read()
            docp = DocHTMLParser(data, fname)
            del data
            self.document = docp.document

    def write_xhtml(self, name):
        if self.document is None:
            return
        with open(name, 'w', encoding='utf-8') as ofile:
            ofile.write("""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n
""")
            write_tags(self.document, ofile)

    def process(self):
        glbs = self.globs
        doc = self.document
        doc['attrs'] = {'xmlns': "http://www.w3.org/1999/xhtml"}
        data = doc['data']
        head, body = None, None
        for i in data:
            if type(i) == str:
                continue
            if i['tag'] == 'head':
                head = i
            if i['tag'] == 'body':
                body = i
        if head is None:
            print('head eq None')
            head = {'tag': 'head', 'data': []}
            data.insert(0, head)
        data = head['data']
        i = 0
        title = {'tag': 'title', 'data': ['None']}
        for i in data:
            if type(i) == dict and i['tag'] == 'title':
                title = i
        link = {'tag': 'link', 'attrs':
                {'rel': "stylesheet", 'href': "../Styles/stylesheet.css",
                 'type': "text/css", 'charset': "utf-8"}}
        data = ['\n', title, '\n', link, '\n']
        head['data'] = data
        if 'attrs' in head:
            head.pop('attrs')
        if body is None:
            print('It is no <body> in the document')
            exit(1)
        i = 0
        data = body['data']
        imd_dat = []
        while i < len(data):
            if 'drop_nodiv' in glbs and \
                    (type(data[i]) != dict or data[i]['tag'] != 'div'):
                data.pop(i)
            elif (type(data[i]) == str and not data[i].isspace()) or \
                    (type(data[i]) == dict and data[i]['tag'] not in
                     {'div', 'p', 'table', 'ul', 'ol', 'dir', 'hr', 'pre',
                      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'dl'}):
                imd_dat.append(data.pop(i))
            else:
                if imd_dat:
                    data.insert(i, {'tag': 'div', 'data': imd_dat})
                    imd_dat = []
                    i += 1
                i += 1
        if imd_dat:
            data.append({'tag': 'div', 'data': imd_dat})
        cll = glbs.get('any_class', [])
        idl = glbs.get('any_id', [])
        cld = glbs.get('drop_class', [])
        idd = glbs.get('drop_id', [])
        if idl or cll:
            any_id_cls_leave(body, cll, idl)
        if cld or idd:
            id_cls_drop(body, cld, idd)
        treat_tag(body, glbs)
        treat_ids(body, glbs['IDs'], glbs['IDf'][glbs['cur_num']])
        if 'leave_space' not in glbs:
            i = 0
            data = body['data']
            while i < len(data):
                if type(data[i]) == dict:
                    space_drop(data[i])
                elif data[i].isspace():
                    data.pop(i)
                    continue
                i += 1
            doc['data'] = ['\n', head, '\n', body, '\n']
        return

    def dropleave(self):
        glbs = self.globs
        if self.document is None:
            return
        body = None
        for i in self.document['data']:
            if type(i) == dict and i['tag'] == 'body':
                body = i
        if body is None:
            return
        cll = glbs.get('any_class', [])
        idl = glbs.get('any_id', [])
        cld = glbs.get('drop_class', [])
        idd = glbs.get('drop_id', [])
        if idl or cll:
            any_id_cls_leave(body, cll, idl)
        if cld or idd:
            id_cls_drop(body, cld, idd)
