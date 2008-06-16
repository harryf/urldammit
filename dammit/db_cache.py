#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cachemanager

cache = cachemanager.new_instance()

def load(method):
    """
    Decorator for load method
    """
    def load_wrapper(self, id):
        if not id in cache:
            cache[id] = method(self, id)
        return cache[id]
    
    return load_wrapper

def insert(method):
    """
    Decorator for insert
    """
    def insert_wrapper(self, uri):
        method(self, uri)
        try:
            del cache[uri.id]
        except:
            pass

    return insert_wrapper

def update(method):
    """
    Decorator for insert
    """
    def update_wrapper(self, uri):
        method(self, uri)
        try:
            del cache[uri.id]
        except:
            pass

    return update_wrapper

def delete(method):
    """
    Decorator for delete
    """
    def delete_wrapper(self, id):
        method(self, id)
        try:
            del cache[id]
        except:
            pass

    return delete_wrapper

