#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script for testing yawlib library
Latest version can be found at https://github.com/letuananh/yawlib

Adapted from: https://github.com/letuananh/lelesk

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2016, Le Tuan Anh <tuananh.ke@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2014, yawlib"
__credits__ = ["Le Tuan Anh"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import sys
import os
import argparse
import unittest
from chirptext.leutile import FileTool
from yawlib.wordnetsql import WordNetSQL as WSQL
from yawlib.glosswordnet import XMLGWordNet
from yawlib.glosswordnet import SQLiteGWordNet as GWNSQL
from yawlib.glosswordnet import Gloss
from yawlib.helpers import get_synset_by_id
from yawlib.helpers import get_synset_by_sk
from yawlib.helpers import get_synsets_by_term
from yawlib.helpers import dump_synset, dump_synsets
from yawlib.wntk import combine_glosses

from yawlib.config import YLConfig
WORDNET_30_PATH          = YLConfig.WORDNET_30_PATH
WORDNET_30_GLOSSTAG_PATH = YLConfig.WORDNET_30_GLOSSTAG_PATH
WORDNET_30_GLOSS_DB_PATH = YLConfig.WORDNET_30_GLOSS_DB_PATH
DB_INIT_SCRIPT           = YLConfig.DB_INIT_SCRIPT
MOCKUP_SYNSETS_DATA      = FileTool.abspath('data/test.xml')
GLOSSTAG_NTUMC_OUTPUT    = FileTool.abspath('data/glosstag_ntumc')
GLOSSTAG_PATCH           = FileTool.abspath('data/glosstag_patch.xml')
GLOSSTAG_XML_FILES = [
    os.path.join(YLConfig.WORDNET_30_GLOSSTAG_PATH , 'merged', 'adv.xml')
    ,os.path.join(YLConfig.WORDNET_30_GLOSSTAG_PATH, 'merged', 'adj.xml')
    ,os.path.join(YLConfig.WORDNET_30_GLOSSTAG_PATH, 'merged', 'verb.xml')
    ,os.path.join(YLConfig.WORDNET_30_GLOSSTAG_PATH, 'merged', 'noun.xml')
    ]


########################################################################

def get_wn():
    return WSQL(YLConfig.WORDNET_30_PATH)


def get_gwn():
    return GWNSQL(YLConfig.WORDNET_30_GLOSS_DB_PATH)


class TestHelperMethods(unittest.TestCase):

    def test_dump_synset(self):
        print("Test get synset by ID")
        gwn = get_gwn()
        ss = get_synset_by_id(gwn, '01775535-v')
        self.assertIsNotNone(ss)
        self.assertGreater(len(ss.terms), 0)
        self.assertGreater(len(ss.keys), 0)
        self.assertGreater(len(ss.glosses), 0)
        pass


class TestGlossWordNetSQL(unittest.TestCase):

    def test_get_freq(self):
        # WSQL should support get_tagcount
        db = WSQL(WORDNET_30_PATH)
        c = db.get_tagcount('100002684')
        self.assertEqual(c, 51)

    def test_synset_info(self):
        xmlwn = XMLGWordNet()
        xmlwn.read(MOCKUP_SYNSETS_DATA)

        ss = xmlwn.synsets[1]
        self.assertIsNotNone(ss)
        self.assertEqual(len(ss.raw_glosses), 2)
        self.assertTrue(ss.raw_glosses[0].gloss)

        glosses = combine_glosses(ss.glosses)
        self.assertEqual(len(glosses), 2)
        # for gl in glosses:
        #     print("#\n\t>%s\n\t>%s\n\t>%s\n" % (gl.items, gl.tags, gl.groups))

    def test_get_gloss_synsets(self):
        print("Test get glossed synset(s)")
        db = GWNSQL(YLConfig.WORDNET_30_GLOSS_DB_PATH)
        glosses = db.schema.gloss.select()
        # select glosses
        print("Gloss count: {}".format(len(glosses)))
        print(glosses[:5])
        # select glossitems
        # gitems = db.schema.glossitem.select(columns='id ord gid lemma'.split())
        # print("Glossitem count: {}".format(len(gitems)))
        # print(gitems[:5])
        # fetch all synsets
        # ss = db.all_synsets()
        # print("Synsets: {}".format(len(ss)))
        # print(ss[:5])
        pass

########################################################################


def main():
    unittest.main()


if __name__ == "__main__":
    main()
