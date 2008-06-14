#!/usr/bin/env python
# -*- coding: utf-8 -*-
from couchdb import Server
from uri import URI

class Couch(object):
    
    def __init__(self, config = None):
        self.config = self._default_config(config)
        self.server = Server(config['server'])
        self.bootstrap()
        self.db = self.server[config['database']]

    def load(self, id):
        """
        >>> config = {}
        >>> config['database'] = 'urldammit_test'
        >>> cdb = Couch(config)

        >>> print cdb.load("123abc")
        None
        """
        data = self.db.get(id, None)
        if not data: return None

        uri = URI()

        for k in uri.fieldnames():
            setattr(uri, k, data[k])
        
        return uri


    def insert(self, uri):
        self.db[uri.id] = uri.data()

    # update and insert equivalent
    update = insert

    def delete(self, id):
        pass

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
    

