#!/usr/bin/env python
# -*- coding: utf-8 -*-

cache_cls = dict

def set_cache_impl(cls):
    """
    Set the class of cache we want to create
    API must behave like a dictionary
    """
    global cache_cls
    cache_cls = cls

def new_instance(*args, **kwargs):
    """
    Create a new instance of the current
    cache class
    """
    return cache_cls(*args, **kwargs)

"""
>>> c = new_instance()
>>> isinstance(c, dict)
True
>>> c['foo'] = 'bar'
>>> print c
bar

>>> from lrucache import LRUCache
>>> set_cache_impl(LRUCache)
>>> c1 = new_instance(1000)
>>> isinstance(c1, LRUCache)
True
"""

def _test():
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    _test()
