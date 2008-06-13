#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2, logging, re
import web # web.py
from dammit.lrucache import LRUCache
from dammit.request import *
from dammit.uri import *
from dammit.db.mock import MockDB

import view
from view import render
import config

urls = (
    '/', 'urldammit',
    '/_tools', 'tools',
    '/_tools/addurl', 'tools_addurl',
    '/_tools/checkurl', 'tools_checkurl',
    '/([0-9a-f]{40})', 'urldammit',
    '/find/(.*)', 'find',
    )

db = MockDB()
manager = URIManager(db)

# cache URIs we know about
known = LRUCache(config.KNOWN_CACHE_SIZE)

# cache queries we know nothing about otherwise
# we have to ask couch each time
unknown = LRUCache(config.UNKNOWN_CACHE_SIZE)

class urldammit(object):
    
    def HEAD(self, id):
        u = self._locate(id)
        if not u: return
        if self._redirect(u): return
        self._ok(u)
        
    def GET(self, id = None):
        if not id:
            print "where's my url dammit?"
            return

        u = self._locate(id)
        
        if not u:
            web.notfound()
            return
        
        if self._redirect(u):
            return

        self._ok(u)
        self._render(u)

    validstatus = re.compile("^200|301|404$")
    
    def PUT(self, uri):
        pass

    def POST(self):
        """
        Update couch with status of uri
        """
        def required(input, key):
            val = None
            try:
                val = getattr(input, key)
            except AttributeError:
                web.ctx.status = statusmap[406]
                print "%s parameter required" % key
            return val
        
        i = web.input()

        uri = required(i, 'uri')
        if uri is None: return

        reduceurl = True
        try:
            reduceurl = getattr(i, 'reduceurl').lower() != 'false'
        except:
            pass
        
        uri = reduce_url(uri)

        # allow an explicit delete using a delete
        # parameter (i.e. allow delete via HTML form)
        try:
            delete = getattr(i, 'delete')
            if delete == 'true':
                self.DELETE(URI.hash(uri))
                return
        except:
            pass

        # if it's not a delete, we require a status
        status = required(i, 'status')
        if status is None: return

        if not self.validstatus.match(status):
            self._badrequest("Bad value for status: '%s'" % status)
            return

        tags = unpack_tags(getattr(i, 'tags', []))
        pairs = unpack_pairs(getattr(i, 'pairs', []))
        location = getattr(i, 'location', [])

        try:
            u = manager.register(
                uri,
                int(status),
                tags = tags,
                pairs = pairs,
                location = location
                )

            known[u.id] = u
            if u.id in unknown: del unknown[u.id]
            
            web.http.seeother(
                "%s/%s" % ( web.ctx.home, u.id)
                )
            self._render(u)

        except URIError, e:
            self._badrequest(e.message)
            
        
    def DELETE(self, id):
        manager.delete(id)
        if id in known: del known[id]
        web.ctx.status = statusmap[204]

    def _locate(self, id):
        """
        See what we know about this uri...
        uri is in fact a SHA-1 hash of the uri
        """
        def ithas(key, cache):
            if key in cache:
                return cache[key]
            return None

        u = ithas(id, unknown)
        if u:
            web.notfound()
            return None

        u = ithas(id, known)
        if not u:
            u = manager.load(id)
            
            if not u:
                unknown[id] = True
                web.notfound()
                return None
            
            known[id] = u
        
        return u

    def _ok(self, u):
        web.ctx.status = statusmap[200]
        web.http.lastmodified(u.updated)

    def _redirect(self, u):
        """
        db reports this url is now elsewhere
        return a redirect response
        """
        if u.status == 301:
            web.ctx.status = statusmap[u.status]
            web.header(
                'Location',
                "%s/%s" % ( web.ctx.home, URI.hash(u.location) )
                )
            return True
        
        return False

    def _render(self, u):
        if not u: return
        print pack_response(u)

    def _badrequest(self, msg):
        web.ctx.status = statusmap[400]
        print view.badrequest(reason = msg)

class find(object):
    """
    To help clients find "reduced" urls
    """
    def GET(self, url):
        web.ctx.status = statusmap[303]
        web.header(
            'Location',
            "%s/%s" % ( web.ctx.home, URI.hash(reduce_url(url)) )
            )
        return

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

