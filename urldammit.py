#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
from dammit.couchutils import uri_to_id, put
from dammit.resource import *
from couchdb import Database

urls = (
    '/', 'urldammit',
    '/_tools', 'tools',
    '/(.*)', 'urldammit',

    )

db = Database('http://localhost:5984/urldammit')

class urldammit:
    
    def HEAD(self, uri):
        r = self._locate(uri)
        if not r: return
        if self._redirect(r): return

        

    def GET(self, uri = None):
        
        if not uri:
            print "where's my url dammit?"
            return
        
        r = self._locate(uri)
        if not r: return
        if self._redirect(r): return
        
        print r

    def POST(self):
        i = web.input()
        register_uri(db, i.uri)
        

    def _locate(self, uri):
        r = URI.load(db, uri_to_id(uri))
        if not r:
            web.notfound()
            return None
        return r

    def _redirect(self, r):
        if 300 <= r.status < 400:
            web.ctx.status = r.status
            web.header('Location', r.location)
            return True
        return False


class tools:
    def GET(self):
        print '<form action="/" method="POST">'
        print '<label for="uri">uri:</label><input name="uri" type="text">'
        print '<input type="submit" value="submit">'
        print '</form>'

if __name__ == '__main__':
    web.run(urls, globals() )

