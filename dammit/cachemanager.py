#!/usr/bin/env python
# -*- coding: utf-8 -*-

def dict_constructor():
    return dict()

cache_constructor = dict_constructor

def register_cache_constructor(func):
    """
    Register a function to be called to create
    cache instances - the function should return
    an instance of the cache
    """
    global cache_constructor
    cache_constructor = func

def new_instance():
    """
    Create a new instance of the current cache class 
    """
    return cache_constructor()

def _test():
    """
    >>> c = new_instance()
    >>> isinstance(c, dict)
    True
    >>> c['foo'] = 'bar'
    >>> print c['foo']
    bar
    
    >>> from lrucache import LRUCache
    >>> register_cache_constructor(lambda: LRUCache(1000))
    >>> c1 = new_instance()
    >>> isinstance(c1, LRUCache)
    True
    """
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test()
