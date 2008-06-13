#!/usr/bin/env python
# -*- coding: utf-8 -*-
class MockDB(object):
    def __init__(self):
        self.uris = {}

    def load(self, id):
        return self.uris.get(id, None)

    def insert(self, uri):
        self.uris[uri.id] = uri

    def update(self, uri):
        self.uris[uri.id] = uri

    def delete(self, id):
        del self.uris[id]
