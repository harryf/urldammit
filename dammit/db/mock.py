#!/usr/bin/env python
# -*- coding: utf-8 -*-
class MockDB(object):
    def __init__(self):
        self.uris = {}
        self.stored = []

    def load(self, id):
        return self.uris.get(id, None)

    def store(self, uri):
        self.stored.append(uri)
        self.uris[uri.id] = uri

    def delete(self, id):
        del self.uris[id]
