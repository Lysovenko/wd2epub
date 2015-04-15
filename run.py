#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"get settings and run program"
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
from index_con import get_enc_name, TabOfCont
from os.path import basename, dirname, join, abspath, isdir, isfile
from os import chdir, getcwd, makedirs, system
from doc_glob import DocGlobals
from argparse import ArgumentParser
from hashlib import md5
from html import escape


def get_info():
    parser = ArgumentParser(description='Making epub from web dir.')
    parser.add_argument('indir', help='directory with html files')
    parser.add_argument('epub', help='destination epub file name')
    parser.add_argument('-d', '--keep-dir', dest='rm_dir', default=True,
                        action='store_false', help='keep OEBPS directory')
    parser.add_argument('-f', '--add-fonts', dest='add_fnts', default=False,
                        action='store_true', help='add fonts to epub')
    parser.add_argument('-l', '--no-keep-local-refs', dest='klr', default=True,
                        action='store_false',
                        help='do not keep all local refferences')
    args = parser.parse_args()
    epub_name = basename(args.epub)
    dest_dir = abspath(join(dirname(args.epub), 'OEBPS'))
    if not isdir(args.indir):
        print('ERROR: No sutch directory: "%s"' % args.indir)
        return
    if isfile(dest_dir):
        print('ERROR: Actually dest. dir. "%s" is file' % dest_dir)
        return
    info = DocGlobals({'title': basename(args.indir), 'author': 'Nemo',
                       'publisher': 'wd2epub', 'index': 'index.html',
                       'language': 'en', 'doc_dir': ''})
    chdir(args.indir)
    with open('bibinfo.txt', encoding='utf-8') as bfp:
        for line in bfp:
            if line.isspace():
                continue
            spl = line.split(':', 1)
            if len(spl) < 2:
                info[spl[0].strip().lower()] = ''
            else:
                info[spl[0].strip().lower()] = spl[1].strip()
        bfp.seek(0)
        info['hash'] = md5(bfp.read().encode('utf-8')).hexdigest()
    info['dest_dir'] = dest_dir
    info['epub_name'] = epub_name
    if args.klr:
        info['keep_local_refs'] = 't'
    else:
        info['keep_local_refs'] = 'f'
    if args.add_fnts or info['language'].lower() != 'en':
        info['fonts_required'] = None
    info['rm_dir'] = args.rm_dir
    for field in ('drop_class', 'drop_id', 'screen',
                  'any_class', 'any_id'):
        if field in info:
            info[field] = set(info[field].split())
    if 'screen' in info:
        try:
            info['screen'] = tuple(map(float, info['screen']))
        except:
            print('ERROR: bad screen format')
            return
        if len(info['screen']) != 2:
            print('ERROR: bad screen format')
            return
    if 'class_to_tag' in info:
        dct = {}
        try:
            for i in info['class_to_tag'].split():
                cl, tg = i.split('=')
                dct[cl] = tg
        except:
            print('ERROR: bad class_to_tag format')
            return
        info['class_to_tag'] = dct
    if 'fonts_required' in info:
        info['fonts_required'] = set()
    if info['keep_local_refs'].lower() in {'no', 'false', 'n',
                                           'f', '0', 'dont'}:
        info.pop('keep_local_refs')
    for i in ('title', 'author', 'publisher'):
        info[i] = escape(info[i])
    return info


def run(glb=None):
    if glb is None:
        glb = get_info()
    if glb is None:
        return
    fn = glb['index']
    if not isfile(fn):
        print('ERROR: No sutch file: "%s"' % fn)
        return
    enc_name = get_enc_name(fn)
    toc_pars = TabOfCont(fn, enc_name, glb)
    toc_pars.mk_iref()
    dest_dir = glb['dest_dir']
    epub_name = glb['epub_name']
    if not isdir(dest_dir):
        makedirs(dest_dir)
    glb.treat_text(enc_name)
    if glb.id_warns():
        return
    glb.treat_imgs()
    chdir(dirname(dest_dir))
    glb.make_stylesheet()
    cfn = join(glb['data_dir'], 'core.zip')
    glb.toc_write(join('OEBPS', 'toc.ncx'))
    glb.opf_write(join('OEBPS', 'content.opf'))
    system('cp -f "%s" "%s"' % (cfn, epub_name))
    system('zip -X "%s" OEBPS -rq' % epub_name)
    if glb['rm_dir']:
        system('rm -rf OEBPS')


if __name__ == '__main__':
    run()
