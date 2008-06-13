#!/usr/bin/env python
# -*- coding: utf-8 -*-
class CouchDB(object):
    def __init__(self, server):
        self.server = server

    def load(self, id):
        """
        if kwargs.has_key('pairs'):
        kwargs['pairs'] = expand_dict(kwargs['pairs'])
        """
        pass

    def insert(self, uri):
        pass

    def update(self, uri):
        pass

    def delete(self, id):
        pass

    def bootstrap(self, **kwargs):
        pass

    def purge(self, **kwargs):
        pass


def expand_dict(d):
    """
    Couchdb doesn't directly support storing of hashes
    but can be simulated via a list of key, value pairs
    We have to translate between the two.

    This takes a normal python dict and expands it to
    'couch-ready' form

    >>> d = {'a':1, 'b': 2}
    >>> o = str(expand_dict(d))
    >>> o.find("{'k': 'a', 'v': 1}") != -1
    True
    """
    pairs = []
    if not type(d) == dict:
        return pairs
    for k, v in d.items():
        pairs.append({'k':k, 'v':v})
    return pairs

def contract_dict(pairs):
    """
    Reduces the dict from couch form into a normal
    python dictionary
    >>> pairs = [{'k':'a','v':1}, {'k':'b','v':2}]
    >>> contract_dict(pairs) == {'a':1, 'b': 2}
    True
    """
    d = {}
    try:
        for pair in pairs:
            d[pair['k']] = pair['v']
    except KeyError:
        pass
    return d

def _test():
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test()

