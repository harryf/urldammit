#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decorator methods for the DB to provide a
cache layer upon records in the DB

This is seperate to the cache of known
and unknown URLs maintained by the urldammit
server
"""
import cachemanager

cache = cachemanager.new_instance('db')

def load(method):
    """
    Decorator for load method
    """
    def load_wrapper(self, id):
        try:
            cached = cache[id]
            if cached is not None:
                return cached
        except:
            pass
        
        cache[id] = method(self, id)
        return cache[id]
    
    return load_wrapper

def insert(method):
    """
    Decorator for insert
    """
    def insert_wrapper(self, uri):
        try:
            del cache[uri.id]
        except:
            pass
        method(self, uri)

    return insert_wrapper

def update(method):
    """
    Decorator for insert
    """
    def update_wrapper(self, uri):
        try:
            del cache[uri.id]
        except:
            pass
        method(self, uri)

    return update_wrapper

def delete(method):
    """
    Decorator for delete
    """
    def delete_wrapper(self, id):
        try:
            del cache[id]
        except:
            pass
        method(self, id)

    return delete_wrapper

