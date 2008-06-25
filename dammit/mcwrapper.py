#!/usr/bin/env python
# -*- coding: utf-8 -*-
class MemcachedWrapper(object):
    """
    Wrapper around an memcached.Client object to implement
    parts of a Python map used for caching in urldammit
    
    http://www.tummy.com/Community/software/python-memcached/

    >>> import memcache
    >>> mc = memcache.Client(['127.0.0.1:11211'])
    >>> mcw = MemcachedWrapper(mc)
    >>> 'foo' in mcw
    False
    >>> mcw['foo'] = 'bar'
    >>> 'foo' in mcw
    True
    >>> mcw['foo'] == 'bar'
    True
    >>> del mcw['foo']
    >>> 'foo' in mcw
    False
    """
    def __init__(self, mc):
        self.mc = mc

    def __len__(self):
        raise Exception("Not implemented")
	
    def __contains__(self, key):
        return self.mc.get(key) != None
    
    def __setitem__(self, key, val):
	self.mc.set(key, val)
    
    def __getitem__(self, key):
        val = self.mc.get(key)
        if val == None:
            raise KeyError(key)
        return val
	
    def __delitem__(self, key):
        if self.mc.delete(key) == 0:
            raise KeyError(key)
        
    def __repr__(self):
        return "MemcachedWrapper"

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
