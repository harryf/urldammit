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

def new_instance(namespace):
    """
    Create a new instance of the current cache class
    
    For a shared cache (e.g. memcached), we need to
    pass some identifier to prevent keys colliding
    hence the namespace param (e.g. use as key prefix
    for memcached impl)
    """
    return cache_constructor(namespace)

def namespacer(func):
    """
    Decorator for injecting a namespace prefix into
    the key argument, obtained from self.namespace
    """
    def namespace_wrapper(self, key, *args, **kwargs):
        key = "%s_%s" % ( self.namespace, key )
        return func( self, key, *args, **kwargs )
    return namespace_wrapper

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
