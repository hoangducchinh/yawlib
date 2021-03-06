#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Gloss WordNet Data Transfer Object
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
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

from yawlib.models import Synset
from chirptext.leutile import StringTool

#-----------------------------------------------------------------------
# CONFIGURATION
#-----------------------------------------------------------------------


class GlossRaw:
    ''' Raw glosses extracted from WordNet Gloss Corpus.
        Each synset has a orig_gloss, a text_gloss and a wsd_gloss
    '''

    # Categories
    ORIG = 'orig'
    TEXT = 'text'

    def __init__(self, synset, cat, gloss):
        self.synset = synset
        self.cat = StringTool.strip(cat)
        self.gloss = StringTool.strip(gloss)

    def __str__(self):
        return "[gloss-%s] %s" % (self.cat, self.gloss)


class GlossedSynset(Synset):
    ''' Each synset object comes with sensekeys (ref: SenseKey), terms (ref: Term), and 3 glosses (ref: GlossRaw).
    '''

    def __init__(self, sid, keys=None, lemmas=None, defs=None, exes=None):
        super().__init__(sid, keys, lemmas, defs, exes)
        self.raw_glosses = []  # list of GlossRaw
        self.glosses = []      # list of Gloss

    def add_raw_gloss(self, cat, gloss):
        gr = GlossRaw(self, cat, gloss)
        self.raw_glosses.append(gr)

    def add_gloss(self, origid, cat, gid=-1):
        g = Gloss(self, origid, cat, gid)
        self.glosses.append(g)
        return g

    def get_orig_gloss(self):
        for gr in self.raw_glosses:
            if gr.cat == 'orig':
                return gr.gloss
        return ''

    def get_gramwords(self, nopunc=True):
        words = []
        for gloss in self.glosses:
            words.extend(gloss.get_gramwords(nopunc))
        return words

    def get_tags(self):
        keys = []
        for gloss in self.glosses:
            keys.extend(gloss.get_tagged_sensekey())
        return keys

    def __getitem__(self, name):
        return self.glosses[name]

    def __repr__(self):
        if self.lemmas is not None and len(self.lemmas) > 0:
            return "{sid} ({lemma})".format(sid=self.sid.to_canonical(), lemma=self.lemmas[0])
        else:
            return "(GSynset:{})".format(self.sid)

    def __str__(self):
        return repr(self)


class Gloss:
    def __init__(self, synset, origid, cat, gid):
        self.synset = synset
        self.gid = gid
        self.origid = origid  # Original ID from Gloss WordNet
        self.cat = cat
        self.items = []       # list of GlossItem objects
        self.tags = []        # Sense tags
        self.groups = []      # Other group labels
        pass

    def get_tagged_sensekey(self):
        return [x.sk for x in self.tags if x]

    def get_gramwords(self, nopunc=True):
        tokens = []
        for item in self.items:
            words = [x for x in item.get_gramwords(nopunc) if x]
            tokens.extend(words)
        return tokens

    def add_gloss_item(self, tag, lemma, pos, cat, coll, rdf, origid, sep=None, text=None, itemid=-1):
        gt = GlossItem(self, tag, lemma, pos, cat, coll, rdf, origid, sep, text, itemid)
        gt.order = len(self.items)
        self.items.append(gt)
        return gt

    def tag_item(self, item, cat, tag, glob, glemma, glob_id, coll, origid, sid, sk, lemma, tagid=-1):
        tag = SenseTag(item, cat, tag, glob, glemma, glob_id, coll, origid, sid, sk, lemma, tagid)
        self.tags.append(tag)
        return tag

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        return self.items[idx]

    def text(self):
        return ' '.join([x.text for x in self.items]).replace(' ;', ';')

    def __repr__(self):
        return "gloss-%s" % (self.cat)

    def __str__(self):
        return "{Gloss('%s'|'%s') %s}" % (self.origid, self.cat, self.text())


class GlossItem:
    ''' A word token (belong to a gloss)
    '''
    def __init__(self, gloss, tag, lemma, pos, cat, coll, rdf, origid, sep=None, text=None, itemid=-1):
        self.itemid = itemid
        self.gloss = gloss
        self.order = -1
        self.tag = StringTool.strip(tag)
        self.lemma = StringTool.strip(lemma)
        self.pos = StringTool.strip(pos)
        self.cat = StringTool.strip(cat)
        self.coll = StringTool.strip(coll)
        self.rdf = StringTool.strip(rdf)
        self.sep = StringTool.strip(sep)
        self.text = StringTool.strip(text)
        self.origid = StringTool.strip(origid)
        pass

    def get_lemma(self):
        return self.text if self.text else self.lemma

    def get_gramwords(self, nopunc=True):
        '''
        Return grammatical words from lemma
        E.g.
        prefer%2|preferred%3 => ['prefer', 'preferred']
        '''
        if nopunc and self.cat == 'punc':
            return set()
        lemmata = set()
        if self.lemma is not None and len(self.lemma) > 0:
            tokens = self.lemma.split('|')
            for token in tokens:
                parts = token.split("%")
                lemmata.add(parts[0])
        return lemmata

    def __repr__(self):
        # return "l:`%s'" % (self.get_lemma())
        return "'%s'" % self.get_lemma()

    def __str__(self):
        return "(itemid: %s | id:%s | tag:%s | lemma:%s | pos:%s | cat:%s | coll:%s | rdf: %s | sep:%s | text:%s)" % (
            self.itemid, self.origid, self.tag, self.lemma, self.pos, self.cat, self.coll, self.rdf, self.sep, self.text)


class GlossGroup:
    ''' A group tag (i.e. labelled GlossItem group)
    '''

    def __init__(self, label=''):
        self.label = label
        self.items = []    # List of GlossItem belong to this group


class SenseTag:
    ''' Sense annotation object
    '''
    def __init__(self, item, cat, tag, glob, glemma, glob_id, coll, origid, sid, sk, lemma, tagid=-1):
        self.tagid = tagid         # tag id
        self.cat = cat             # coll, tag, etc.
        self.tag = tag             # from glob tag
        self.glob = glob           # from glob tag
        self.glemma = glemma       # from glob tag
        self.glob_id = glob_id     # from glob tag
        self.coll = coll           # from cf tag
        self.origid = origid       # from id tag
        self.sid = sid             # infer from sk & lemma
        self.gid = item.gloss.gid  # gloss ID
        self.sk = sk               # from id tag
        self.lemma = lemma          # from id tag
        self.item = item            # ref to gloss item (we can access gloss obj via self.item)

    def __repr__(self):
        return "%s (sk:%s)" % (self.lemma, self.sk)

    def __str__(self):
        return "%s (sk:%s | itemid: %s | cat:%s | tag:%s | glob:%s | glemma:%s | gid:%s | coll:%s | origid: %s)" % (
            self.lemma, self.sk, self.item.itemid, self.cat, self.tag, self.glob, self.glemma, self.glob_id, self.coll, self.origid)
