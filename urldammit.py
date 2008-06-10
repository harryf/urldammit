#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
import urllib2
import logging
import re
from dammit.couchutils import uri_to_id, put, delete
from dammit.resource import *
from dammit.lrucache import LRUCache
from couchdb import Database
from dammit.http import statusmap
from dammit.request import unpack_tags, unpack_pairs, pack_response
import view
from view import render
import config

urls = (
    '/', 'urldammit',
    '/_tools', 'tools',
    '/_tools/addurl', 'tools_addurl',
    '/_tools/checkurl', 'tools_checkurl',
    '/([0-9a-f]{40})', 'urldammit',
    )

db = Database(config.DBURL)

# cache URIs we know about
known = LRUCache(config.KNOWN_CACHE_SIZE)

# cache queries we know nothing about otherwise
# we have to ask couch each time
unknown = LRUCache(config.UNKNOWN_CACHE_SIZE)

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

    validstatus = re.compile("^[1-5][0-9]{2}$")
    
    def PUT(self, uri):
        pass

    def POST(self):
        """
        Update couch with status of uri
        """
        i = web.input()

        uri = self._reqd(i, 'uri')
        if uri is None: return

        status = self._reqd(i, 'status')

        # status not supplied? acts as a DELETE
        # (i.e. allow delete via HTML form)
        if status is None or status == "":
            logging.debug("proxy delete via post")
            self.DELETE(uri)
            return

        if not self.validstatus.match(status):
            self._badrequest("Bad value for status: '%s'" % status)
            return

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

        id = uri_to_id(i.uri)
        if r:
            known[id] = r
            web.http.seeother(
                "%s/%s" % ( web.ctx.home, id)
                )
        self._render(r)
            
        
    def DELETE(self, uri):
        try:
            u = URI.load(db, uri_to_id(uri))
            if not u:
                logging.warn("DELETE called for id %s - not found" % uri)
            db.resource.delete(db, uri, u.rev)
        except Exception, e:
            """
            couchdb issue... (doesn't actually delete)
            'Document rev/etag must be specified to delete'
            """
            logging.error(e)
        
        web.ctx.status = statusmap[204]

    def _locate(self, uri):
        """
        See what we know about this uri...
        uri is in fact a SHA-1 hash of the uri
        """
        def ithas(key, cache):
            if key in cache:
                return cache[key]
            return None

        u = ithas(uri, unknown)
        if u:
            web.notfound()
            return None

        r = ithas(uri, known)
        if not r:
            r = URI.load(db, uri)
            
            if not r:
                unknown[uri] = True
                web.notfound()
                return None
            
            known[uri] = r
        
        return r

    def _ok(self, r):
        web.ctx.status = statusmap[200]
        web.http.lastmodified(r.updated)

    def _redirect(self, r):
        """
        couch reports this url is now elsewhere
        return a redirect response
        """
        if 300 <= r.status < 400:
            if r.status in status:
                web.ctx.status = statusmap[r.status]
                web.header(
                    'Location',
                    "%s/%s" % ( web.ctx.home, uri_to_id(r.location) )
                    )
                return True
        return False

    def _reqd(self, input, key):
        val = None
        try:
            val = getattr(input,key)
        except AttributeError:
            web.ctx.status = statusmap[406]
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

    def _badrequest(self, msg):
        web.ctx.status = statusmap[400]
        print view.badrequest(reason = msg)
        

class tools:
    def GET(self):
        print render.base(view.tools())

class tools_addurl:
    def GET(self):
        print render.base(view.addurl())

class tools_checkurl:
    def GET(self):
        print render.base(view.checkurl())

if __name__ == '__main__':
    import logging, sys
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) > 1 and sys.argv[1] == "webtest":
        import dammit.webtests
        dammit.webtests.run()
    else:
        web.webapi.internalerror = web.debugerror
        web.run(urls, globals() )

