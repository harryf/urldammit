#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
import urllib2
import logging
from dammit.couchutils import uri_to_id, put, delete
from dammit.resource import *
from dammit.lrucache import LRUCache
from couchdb import Database
from dammit.http import status
from dammit.request import unpack_tags, unpack_pairs, pack_response

urls = (
    '/', 'urldammit',
    '/_tools', 'tools',
    '/(.*)', 'urldammit',
    )

db = Database('http://localhost:5984/urldammit')

# cache URIs we know about
known = LRUCache(1000)

# cache queries we know nothing about otherwise
# we have to ask couch each time
unknown = LRUCache(100)

class urldammit:
    
    def HEAD(self, uri):
        r = self._locate(uri)
        if not r: return
        if self._redirect(r): return
        self._ok(r)
        
    def GET(self, uri = None):
        if not uri:
            print "where's my url dammit?"
            return
        
        r = self._locate(uri)
        
        if not r: return
        if self._redirect(r): return

        self._ok(r)
        self._render(r)

    def POST(self):
        """
        Update couch with status of uri
        """
        i = web.input()

        uri = self._reqd(i, 'uri')
        if uri is None: return

        status = self._reqd(i, 'status')
        if status is None: return
        # todo validate numeric

        try:
            logging.debug('tags: %s', i.tags)
        except:
            logging.debug('tags not found')

        tags = getattr(i, 'tags', [])
        if tags:
            tags = unpack_tags(tags)

        logging.debug('tags unpacked: %s', tags)

        try:
            logging.debug('pairs: %s', i.tags)
        except:
            logging.debug('pairs not found')
        
        pairs = getattr(i, 'pairs', [])
        logging.debug(pairs)
        if pairs:
            pairs = unpack_pairs(pairs)

        logging.debug('pairs unpacked: %s', pairs)
        
        r = register_uri(db, uri = uri, status = int(status),\
                         tags = tags, pairs = pairs )
        if r: known[id] = r
        web.http.seeother("%s/%s" % ( web.ctx.home, urllib2.quote(i.uri)) )
        self._render(r)
            
        
    def DELETE(self):
        i = web.input()
        uri = self._reqd(i, 'uri')
        if not uri: return

        delete(db, id)
        web.ctx.status = status[204]

    def _locate(self, uri):
        """
        See what we know about this uri...
        """
        id = uri_to_id(uri)

        def ithas(key, cache):
            if key in cache:
                return cache[key]
            return None

        u = ithas(id, unknown)
        if u:
            web.notfound()
            return None

        r = ithas(id, known)
        if not r:
            r = URI.load(db, id)
            
            if not r:
                unknown[id] = True
                web.notfound()
                return None
            
            known[id] = r
        
        return r

    def _ok(self, r):
        web.ctx.status = status[200]
        web.http.lastmodified(r.updated)

    def _redirect(self, r):
        """
        couch reports this url is now elsewhere
        return a redirect response
        """
        if 300 <= r.status < 400:
            if r.status in status:
                web.ctx.status = status[r.status]
                web.header('Location', r.location)
                return True
        return False

    def _reqd(self, input, key):
        val = None
        try:
            val = getattr(input,key)
        except AttributeError:
            web.ctx.status = status[406]
            print "%s parameter required" % input
        return val

    def _render(self, r):
        if not r:
            return
        
        response = {
            'uri': r.uri,
            'status': r.status,
            'created': str(r.created),
            'updated': str(r.updated),
            'tags': r.tags,
            'pairs': r.pairs.list,
            }

        response['id'] = uri_to_id(r.uri)

        if r.location:
            response['location'] = r.location
        else:
            response['location'] = r.uri

        print pack_response(response)


class tools:
    def GET(self):
        print '<form action="/" method="POST">'
        print '<label for="uri">uri:</label><input name="uri" type="text"><br>'
        print '<label for="status">status:</label><input name="status" type="text"><br>'
        print '<label for="tags">tags:</label><input name="tags" type="text"><br>'
        print '<label for="pairs">pairs:</label><input name="pairs" type="text"><br>'
        print '<input type="submit" value="submit">'
        print '</form>'

if __name__ == '__main__':
    import logging, sys
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) > 1 and sys.argv[1] == "webtest":
        import dammit.webtests
        dammit.webtests.run()
    else:
        web.webapi.internalerror = web.debugerror
        web.run(urls, globals() )

