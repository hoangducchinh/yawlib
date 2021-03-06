#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Shared data models
Latest version can be found at https://github.com/letuananh/yawlib

Adapted from: https://github.com/letuananh/lelesk

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2014, Le Tuan Anh <tuananh.ke@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2014, lelesk"
__credits__ = ["Le Tuan Anh"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import json
import re
from chirptext.leutile import uniquify

########################################################################


class POS(object):
    NOUN = 1
    VERB = 2
    ADJECTIVE = 3
    ADVERB = 4
    ADJECTIVE_SATELLITE = 5
    EXTRA = 6

    NUMS = '123456'
    POSES = 'nvarsx'
    num2pos_map = dict(zip(NUMS, POSES))
    pos2num_map = dict(zip(POSES, NUMS))

    def num2pos(pos_num):
        if pos_num not in POS.num2pos_map:
            raise Exception('Invalid POS number')
        return POS.num2pos_map[pos_num]

    def pos2num(pos):
        if pos not in POS.pos2num_map:
            raise Exception('Invalid POS')
        else:
            return POS.pos2num_map[pos]


class SynsetID(object):

    WNSQL_FORMAT = re.compile(r'(?P<pos>[123456nvarsx])(?P<offset>\d{8})')
    CANONICAL_FORMAT = re.compile(r'(?P<offset>\d{8})-?(?P<pos>[nvasrx])')

    def __init__(self, offset, pos):
        self.offset = offset
        self.pos = pos

    @staticmethod
    def from_string(synsetid):
        if synsetid is None:
            raise Exception("synsetid cannot be None")
        m = SynsetID.WNSQL_FORMAT.match(str(synsetid))
        if m:
            # WNSQL_FORMAT
            offset = m.group('offset')
            pos = m.group('pos')
            if pos in POS.NUMS:
                pos = POS.num2pos(pos)
            return SynsetID(offset, pos)
        else:
            # try canonical format
            m = SynsetID.CANONICAL_FORMAT.match(str(synsetid))
            if m:
                offset = m.group('offset')
                pos = m.group('pos')
                return SynsetID(offset, pos)
            else:
                raise Exception("Invalid synsetid format (provided: {})".format(synsetid))

    def to_canonical(self):
        ''' Wordnet synset ID (canonical format: 12345678-x)
        '''
        return "{offset}-{pos}".format(offset=self.offset, pos=self.pos)

    def to_wnsql(self):
        '''WordNet SQLite synsetID format (112345678)
           Reference: https://sourceforge.net/projects/wnsql/'''
        return "{posnum}{offset}".format(offset=self.offset, posnum=POS.pos2num(self.pos))

    def to_gwnsql(self):
        '''Gloss WordNet SQLite synsetID format (x12345678)'''
        return "{pos}{offset}".format(offset=self.offset, pos=self.pos)

    def __hash__(self):
        return hash(self.to_canonical())

    def __eq__(self, other):
        # make sure that the other instance is a SynsetID object
        if other and not isinstance(other, SynsetID):
            other = SynsetID.from_string(str(other))
        return other is not None and self.offset == other.offset and self.pos == other.pos

    def __repr__(self):
        return self.to_canonical()

    def __str__(self):
        return repr(self)


class Synset(object):

    def __init__(self, sid, keys=None, lemmas=None, defs=None, exes=None, tagcount=0, lemma=None):
        self.synsetid = sid
        self.keys = keys if keys is not None else []
        self.lemmas = lemmas if lemmas is not None else []
        self.defs = defs if defs else []
        self.exes = exes if exes else []
        self.tagcount = tagcount
        if lemma is not None:
            self.lemma = lemma  # Canonical lemma
        pass

    @property
    def definition(self):
        if self.defs is not None and len(self.defs) > 0:
            return self.defs[0]

    @definition.setter
    def definition(self, value):
        if self.defs is None:
            self.defs = []
        elif len(self.defs) == 0:
            self.defs.append(value)
        else:
            self.defs[0] = value

    @property
    def synsetid(self):
        ''' An alias of sid '''
        return self.sid

    @synsetid.setter
    def synsetid(self, value):
        self.sid = SynsetID.from_string(value)

    @property
    def lemma(self):
        ''' Synset canonical lemma '''
        if self.lemmas is None or len(self.lemmas) == 0:
            return None
        else:
            return self.lemmas[0]

    @lemma.setter
    def lemma(self, value):
        if value is None:
            raise Exception("Canonical lemma cannot be None")
        if self.lemmas is None:
            self.lemmas = [value]
        elif len(self.lemmas) == 0:
            self.lemmas.append(value)
        else:
            self.lemmas[0] = value

    def add_lemma(self, value):
        if self.lemmas is None:
            self.lemmas = []
        self.lemmas.append(value)

    def add_key(self, key):
        self.keys.append(key)

    def get_tokens(self):
        tokens = []
        tokens.extend(self.lemmas)
        for l in self.lemmas:
            if ' ' in l:
                tokens.extend(l.split())
        return uniquify(tokens)

    def to_json(self):
        return {'synsetid': self.synsetid.to_canonical(),
                'definition': self.definition,
                'lemmas': self.lemmas,
                'sensekeys': self.keys,
                'tagcount': self.tagcount,
                'examples': self.exes}

    def to_json_str(self):
        return json.dumps(self.to_json())

    def __str__(self):
        return "(Synset:{})".format(self.sid)


class SynsetCollection(object):
    ''' Synset collection which provides basic synset search function (by_sid, by_sk, etc.)
    '''
    def __init__(self):
        self.synsets = []
        self.sid_map = {}
        self.sk_map = {}

    def add(self, synset):
        ssid = synset.sid
        self.synsets.append(synset)
        self.sid_map[ssid] = synset
        if synset.keys is not None and len(synset.keys) > 0:
            for key in synset.keys:
                self.sk_map[key] = synset
        return self

    def __getitem__(self, name):
        return self.synsets[name]

    def by_sid(self, sid):
        if sid and sid in self.sid_map:
            return self.sid_map[str(sid)]
        else:
            return None

    def by_sk(self, sk):
        if sk in self.sk_map:
            return self.sk_map[sk]
        else:
            return None

    def __iter__(self):
        return iter(self.synsets)

    def count(self):
        return len(self.synsets)

    def __len__(self):
        return self.count()

    def merge(self, another_scol):
        ''' Add synsets from another synset collection '''
        for synset in another_scol.synsets:
            self.add(synset)
        return self

    def __str__(self):
        return str(self.synsets)

    def to_json(self):
        return [x.to_json() for x in self]

    def to_json_str(self):
        return json.dumps(self.to_json())


########################################################################

def main():
    print("This is a library, not a tool")


if __name__ == "__main__":
    main()
