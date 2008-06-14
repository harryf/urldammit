#!/usr/bin/env python
# -*- coding: utf-8 -*-
from couchdb import Server
from uri import URI
from lrucache import LRUCache

class Couch(object):
    """
    >>> config = {}
    >>> config['database'] = 'urldammit_test'
    >>> cdb = Couch(config)
    >>> del cdb.server['urldammit_test']
    >>> cdb = Couch(config)
    
    >>> print cdb.load("123abc")
    None
    >>> u = URI()
    >>> u.status = 200
    >>> u.uri = "http://local.ch/load_1.html"
    >>> cdb.insert(u)
    
    >>> u1 = cdb.load(u.id)
    >>> u1.uri == u.uri
    True
    >>> print u1.uri
    http://local.ch/load_1.html
    >>> cdb.delete(u.id)

    >>> cdb.insert(u)
    >>> u2 = cdb.load(u.id)
    >>> u2.uri == u.uri
    True
    >>> cdb.delete(u.id)

    >>> cdb.insert(u)
    >>> u.tags = ['foo','bar']
    >>> cdb.update(u)
    >>> u3 = cdb.load(u.id)
    >>> print u3.tags
    ['foo', 'bar']

    >>> del cdb.server['urldammit_test']
    """
    def __init__(self, config = None):
        self.cache = LRUCache(1000)
        self.config = self._default_config(config)
        self.server = Server(config['server'])
        self.bootstrap()
        self.db = self.server[config['database']]

    def load(self, id):
        record = self._load(id)
        if not record:
            return None

        data = {}
        for k, v in record.items():
            k = k.encode('utf-8')
            if isinstance(v, unicode):
                data[k] = v.encode('utf-8')
            elif k == 'tags':
                try:
                    data[k] = [tag.encode('utf-8') for tag in v]
                except:
                    data[k] = None
            elif k == 'pairs':
                data[k] = contract_dict(v)
            else:
                data[k] = v
        
        return URI.load(data)


    def insert(self, uri):
        self.db[uri.id] = uri.data()
        if uri.id in self.cache:
            del self.cache[uri.id]

    def update(self, uri):
        data = self._load(uri.id)
        if not data: self.insert(uri)
        
        for k, v in uri.data().items():
            data[k] = v
        self.db[uri.id] = data
        self.cache[uri.id] = data

    def delete(self, id):
        del self.db[id]
        if id in self.cache:
            del self.cache[id]

    def bootstrap(self, **kwargs):
        dbname = self.config['database']
        if not dbname in self.server:
            self.server.create(dbname)
            

    def purge(self, **kwargs):
        pass

    def _default_config(self, config):
        """
        Setup default values for configuration
        """
        if not config: config = {}
        config['server'] = config.get('server', 'http://localhost:5984')
        config['database'] = config.get('database', 'urldammit')
        return config

    def _load(self, id):
        if not id in self.cache:
            self.cache[id] = self.db.get(id, None)
        return self.cache[id]

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
    if pairs is None: return None
    d = {}
    try:
        for pair in pairs:
            k = pair['k'].encode('utf-8')
            if isinstance(pair['v'], unicode):
                d[k] = pair['v'].encode('utf-8')
            else:
                d[k] = pair['v']
    except KeyError:
        pass
    if len(d.keys()) > 0:
        return d
    return None

def _test():
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test()
    

