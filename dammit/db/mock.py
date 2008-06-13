#!/usr/bin/env python
# -*- coding: utf-8 -*-
class MockDB(object):
    def __init__(self):
        self.uris = {}

    def load(self, id):
        """
        Takes a SHA-1 id
        """
        return self.uris.get(id, None)

    def insert(self, uri):
        """
        Takes a URI object
        """
        self.uris[uri.id] = uri

    def update(self, uri):
        """
        Takes a URI object
        """
        self.uris[uri.id] = uri

    def delete(self, id):
        """
        Takes a SHA-1 id
        """
        del self.uris[id]

    def bootstrap(self, **kwargs):
        """
        Setup the database, tables etc.
        """
        pass

    def purge(self, **kwargs):
        """
        Clean up old data
        """
        pass
5        

