#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
For tests - a cache which doesn't remember
anything
"""
from cachemanager import namespacer

class NullCache(object):
    """
    >>> nc = NullCache()
    >>> 'foo' in nc
    False
    >>> nc['foo'] = 'bar'
    >>> 'foo' in nc
    False
    >>> nc['foo'] == 'bar'
    Traceback (most recent call last):
    KeyError: '_foo'
    >>> del nc['foo']
    Traceback (most recent call last):
    KeyError: '_foo'
    """
    def __init__(self):
        self.namespace = ''
    
    def __len__(self):
        raise Exception("Not implemented")

    @namespacer
    def __contains__(self, key):
        return False

    @namespacer
    def __setitem__(self, key, val):
	pass

    @namespacer
    def __getitem__(self, key):
        raise KeyError(key)

    @namespacer
    def __delitem__(self, key):
        raise KeyError(key)
    
    def __repr__(self):
        return "NullCache"

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
