#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"make cascade stylesheet"
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


from os.path import isfile, isdir, join, dirname, abspath
from os import listdir, makedirs, popen, system
from pg_pars import HTMLDocument


class DocGlobals(dict):
    def __init__(self, *args):
        dict.__init__(self, *args)
        for i in ('imgs', 'img_szs', 'docs', 'IDr', 'IDf', 'reflist', 'IDs'):
            self[i] = self.get(i, [])
        self['data_dir'] = abspath(dirname(__file__))

    def id_warns(self):
        errors_found = False
        for idr, idf, fnam in zip(self['IDr'], self['IDf'], self['docs']):
            for i in idr:
                if i not in idf:
                    print('\x1b[1;33mWARNING:\x1b[0m fragment identifier "%s"\
 is not defined in "%s"' % (self['IDs'][i], fnam))
            cnts = {}
            for i in idf:
                if i in cnts:
                    cnts[i] += 1
                else:
                    cnts[i] = 1
            for i in cnts:
                if cnts[i] > 1:
                    print('\x1b[1;31mERROR:\x1b[0m fragment identifier "%s"\
 fount %d times in "%s"' % (self['IDs'][i], cnts[i], fnam))
                    errors_found = True
        return errors_found

    def make_stylesheet(self):
        if 'fonts_required' in self:
            font_desc = {}
            fnt_arch = join(self['data_dir'], 'fonts.zip')
            with popen('unzip -p "%s" description.txt'
                       % fnt_arch) as desc:
                for line in desc:
                    if ':' in line:
                        spl = line.split(':')
                        font_desc[spl[0].strip()] = spl[1].strip()
        fn = 'OEBPS/Styles/stylesheet.css'
        if not isdir('OEBPS/Styles'):
            makedirs('OEBPS/Styles')
        with open(fn, 'w') as fout:
            if 'fonts_required' in self:
                if not isdir('OEBPS/Fonts'):
                    makedirs('OEBPS/Fonts')
                desc_l = {'r': 'regular', 'b': 'bold', 'n': 'normal',
                          'i': 'italic', 'm': 'monospace'}
                for font_type in self['fonts_required']:
                    if font_type not in font_desc:
                        print('warning: lack of %s font' % font_type)
                        continue
                    fnt_fam = desc_l[font_type[0]]
                    fnt_wght = desc_l[font_type[1]]
                    fnt_st = desc_l[font_type[2]]
                    fsrc = font_desc[font_type]
                    fout.write("""
@font-face {
font-family: "%s";
font-weight: %s;
font-style: %s;
src:url(../Fonts/%s);
}
""" % (fnt_fam, fnt_wght, fnt_st, fsrc))
                    system('unzip -q "%s" "%s" -d OEBPS/Fonts' %
                           (fnt_arch, fsrc))
                fout.write("""
body {font-family: "regular";}
pre {font-family: "monospace";}
tt {font-family: "monospace";}
code {font-family: "monospace";}
""")
            # if write_body:
            #     fout.write('body { margin: 0pt; }\n')
            fout.write("""h1 { text-align: center; font-weight: bold;}
h2 { text-align: center; font-weight: bold;}
h3 { text-align: center; font-weight: bold;}
h4 { text-align: center; font-weight: bold;}
h5 { text-align: center; font-weight: bold;}
h6 { text-align: center; font-weight: bold;}
p {
    margin-left: 0ex;
    text-indent: 3ex;
    margin-bottom: 0;
    margin-top: 0;
    text-align: justify;
}
center {margin-left:auto; margin-right:auto; }
""")
        if isdir('OEBPS/Fonts'):
            ffl = []
            for i, nam in enumerate(listdir('OEBPS/Fonts'), 1):
                ffl.append('<item id="font_%d" href="Fonts/%s" \
media-type="application/x-font-ttf"/>\n' % (i, nam))
            self['font_files'] = ''.join(ffl)

    def treat_text(self, enc_name):
        text_dir = join(self['dest_dir'], 'Text')
        if not isdir(text_dir):
            makedirs(text_dir)
        tfn_pat = join(text_dir, 'ht_%d.xhtml')
        ndocs = len(self['docs'])
        for num, fnam in enumerate(self['docs']):
            outfn = tfn_pat % num
            self['doc_dir'] = dirname(fnam)
            self['cur_num'] = num
            print('(%d of %d)' % (num + 1, ndocs), fnam)
            doc = HTMLDocument(fnam, enc_name, self)
            doc.process()
            doc.write_xhtml(outfn)

    def treat_imgs(self):
        imag_dir = join(self['dest_dir'], 'Images')
        if self['imgs'] and not isdir(imag_dir):
            makedirs(imag_dir)
        tfn_pat = join(imag_dir, 'i_%d.png')
        cmd_pat = 'convert "%%s"  -channel RGBA \
-matte -colorspace gray "%s"' % tfn_pat
        cmd1_pat = 'convert "%%s"  -channel RGBA \
-matte -colorspace gray -resize %%dx%%d "%s"' % tfn_pat
        print()
        nimgs = len(self['imgs'])
        for num, (fnam, rsz) in enumerate(zip(self['imgs'], self['img_szs'])):
            if isfile(tfn_pat % num):
                continue
            if rsz:
                system(cmd1_pat % ((fnam,) + rsz + (num,)))
                print("\x1b[1A\x1b[2K(%d of %d) %s (%dx%d)" %
                      ((num + 1, nimgs, fnam) + rsz))
            else:
                system(cmd_pat % (fnam, num))
                print("\x1b[1A\x1b[2K(%d of %d) %s" % (num + 1, nimgs, fnam))

    def toc_write(self, nam):
        itms = self['reflist']
        depth = max([i[3] for i in itms])
        toc = open(nam, 'w', encoding='utf-8')
        toc.write("""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
   "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">

<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head>
<meta name="dtb:uid" content="%s"/>
<meta name="dtb:depth" content="%d"/>
<meta name="dtb:totalPageCount" content="0"/>
<meta name="dtb:maxPageNumber" content="0"/>
</head>
<docTitle>
<text>%s</text>
</docTitle>
<navMap>
""" % (self['hash'], depth, self['title']))
        depth = 0
        plord = 0
        pord = 0
        prev = ''
        for nl, (pos, lab, nam, lr) in enumerate(itms, 1):
            while depth >= lr:
                toc.write('</navPoint>\n')
                depth -= 1
            src = 'Text/ht_%d.xhtml' % pos
            if lab >= 0:
                src = '%s#x%x' % (src, lab)
            if src != prev:
                prev = src
                pord += 1
            # src = escape(src)
            toc.write('<navPoint id="navPoint-%d" \
playOrder="%d">\n' % (nl, pord))
            toc.write("""<navLabel>
<text>%s</text>
</navLabel>
<content src="%s"/>
""" % (nam, src))
            depth += 1
        while depth:
            toc.write('</navPoint>\n')
            depth -= 1
        toc.write('</navMap>\n</ncx>\n')
        toc.close()

    def opf_write(self, nam):
        try:
            opf = open(nam, 'w', encoding='utf-8')
        except IOError:
            return
        opf.write("""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" \
version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" \
xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>%(title)s</dc:title>
        <dc:language>%(language)s</dc:language>
        <dc:rights>Public Domain</dc:rights>
        <dc:creator opf:role="aut">%(author)s</dc:creator>
        <dc:publisher>%(publisher)s</dc:publisher>
        <dc:identifier id="BookID" opf:scheme="UUID">%(hash)s</dc:identifier>
        <meta name="Sigil version" content="0.2.4"/>
    </metadata>
    <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        <item id="stylesheet.css" \
href="Styles/stylesheet.css" media-type="text/css"/>
""" % self)
        if 'font_files' in self:
            opf.write(self['font_files'])
        for i in range(len(self['imgs'])):
            opf.write('<item id="i_%d" href="Images/i_%d.png" \
media-type="image/png"/>\n' % (i, i))
        for i in range(len(self['docs'])):
            opf.write('<item id="h_%d" href="Text/ht_%d.xhtml" \
media-type="application/xhtml+xml"/>\n' % (i, i))
        opf.write('</manifest>\n<spine toc="ncx">\n')
        for i in range(len(self['docs'])):
            opf.write('<itemref idref="h_%d"/>\n' % i)
        opf.write('</spine>\n</package>\n')
        opf.close()
