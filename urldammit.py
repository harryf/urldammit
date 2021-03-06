#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2, logging, re
import web
from dammit import cachemanager
from dammit.request import *
from dammit.uri import *
from dammit.log import Log

import view
from view import render
import config

urls = (
    '/', 'urldammit',
    '/_tools/?', 'tools',
    '/_tools/addurl', 'tools_addurl',
    '/_tools/checkurl', 'tools_checkurl',
    '/([0-9a-f]{40})', 'urldammit',
    '/find/(.*)', 'find',
    )

instances = {'manager': None, 'known': None, 'unknown': None}
def make_instance_getter(key, fn):
    def get_instance():
        if instances[key] == None:
            instances[key] = fn()
        return instances[key]
    return get_instance

"""
import sys
if len(sys.argv) > 1 and sys.argv[1] == "webtest":
    print "Running in test mode"
    from dammit.nullcache import NullCache
    get_manager = make_instance_getter('manager', lambda: URIManager(config.get_db_mock()))
    get_known = make_instance_getter('known', lambda: NullCache())
    get_unknown = make_instance_getter('unknown', lambda: NullCache())
    del sys.argv[1]
else:
    get_manager = make_instance_getter('manager', lambda: URIManager(config.get_db()))
    get_known = make_instance_getter('known', lambda: cachemanager.new_instance('known'))
    get_unknown = make_instance_getter('unknown', lambda: cachemanager.new_instance('unknown'))
"""
    
get_manager = make_instance_getter('manager', lambda: URIManager(config.get_db()))
get_known = make_instance_getter('known', lambda: cachemanager.new_instance('known'))
get_unknown = make_instance_getter('unknown', lambda: cachemanager.new_instance('unknown'))

class urldammit(object):
    """
    Main service handler
    """
    
    def HEAD(self, id):
        """
        Check the status of a URI using a HEAD request
        ID is the SHA-1 of the URI
        """
        u = self._locate(id)
        if not u: return
        if not self._redirect(u):
            self._ok(u)
        
    def GET(self, id = None):
        """
        Get the record for a given URI
        ID is the SHA-1 of the URI
        """
        if not id:
            return "where's my url dammit?"

        u = self._locate(id)
        
        if not u:
            return
        
        if not self._redirect(u):
            self._ok(u)
        
        return self._render(u)

    validstatus = re.compile("^200|301|404$")
    
    def PUT(self, id):
        """
        PUT a record of a URI - deletes any existing record
        of the URI and creates a new one.
        Param is the SHA-1 hash of the URL
        Payload is www-form-urlencoded - same as POST except
        delete param is ignored
        """
        i = web.input()
        uri = required(i, 'uri')
        if uri is None: return
        uri = reduce_uri(i, uri)
        self._delete(URI.hash(uri))
        self._store(uri, i)

    def POST(self):
        """
        Update with status of uri. payload is www-form-urlencoded
        
        Params;

        uri: the uri to store (required)
        status: HTTP status (/[0-9]{3}/, required)
        delete: Whether to delete the record (/true|false/)
        tags: JSON encoded list of values obeying /[a-zA-Z0-9[1,50]/
        pairs: JSON encoded key -> value hash - keys object tag rules
        location: if status == 301, the new location to redirect to (required if status == 301)
        """
        i = web.input()

        uri = required(i, 'uri')
        if uri is None: return

        uri = reduce_uri(i, uri)

        # allow an explicit delete using a delete
        # parameter (i.e. allow delete via HTML form)
        try:
            delete = getattr(i, 'delete')
            if delete == 'true':
                self.DELETE(URI.hash(uri))
                return
        except:
            pass

        self._store(uri, i)
        
    def DELETE(self, id):
        """
        Delete a record, given the SHA-1 hash of it's URI
        """
        self._delete(id)
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

        unknown = get_unknown()
        known = get_known()
        
        u = ithas(id, unknown)
        if u:
            web.notfound()
            return None

        u = ithas(id, known)
        if not u:
            u = get_manager().load(id)
            
            
            if not u:
                unknown[id] = True
                web.notfound()
                return None
            
            known[id] = u
        
        return u

    def _store(self, uri, i):
        """
        Store a record
        """
        status = required(i, 'status')
        if status is None:
            return False

        if not self.validstatus.match(status):
            return self._badrequest("Bad value for status: '%s'" % status)

        tags = unpack_tags(getattr(i, 'tags', []))
        pairs = unpack_pairs(getattr(i, 'pairs', {}))
        location = getattr(i, 'location', None)
        known = get_known()
        unknown = get_unknown()

        try:
            u = get_manager().register(
                uri,
                int(status),
                tags = tags,
                pairs = pairs,
                location = location
                )

            known[u.id] = u
            if u.id in unknown:
                del unknown[u.id]

            web.seeother("%s/%s" % (web.ctx.home, u.id))
            return

        except URIError, e:
            return self._badrequest(e)

    def _delete(self, id):
        known = get_known()
        if id in known:
            del known[id]
        get_manager().delete(id)

    def _ok(self, u):
        """
        Return a 200 response
        """
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
        """
        Display result, encoded as json
        """
        if not u: return
        return pack_response(u)

    def _badrequest(self, msg):
        """
        Bad request (e.g. trying to record info on a status 404 url which
        urldammit has never seen before)
        """
        web.ctx.status = statusmap[400]
        return view.badrequest(reason = msg)

class find(object):
    """
    To help clients find "reduced" urls
    """
    def GET(self, url):
        url = reduce_uri(web.input(), url)
        web.ctx.status = statusmap[303]
        web.header(
            'Location',
            "%s/%s" % ( web.ctx.home, URI.hash(url) )
            )

class tools:
    """
    Tools for humans...
    """
    def GET(self):
        return render.base(view.tools())

class tools_addurl:
    def GET(self):
        return render.base(view.addurl())

class tools_checkurl:
    def GET(self):
        return render.base(view.checkurl())

encoded = re.compile('^https?%3A%2F%2F')
def reduce_uri(i, uri):
    """
    Utility fn - shorten the provided
    uri to it's path (and left), if the object
    i contains an attribute reduceurl
    """
    if encoded.match(uri):
        uri = urllib2.unquote(uri)
    
    reduceurl = True
    try:
        reduceurl = getattr(i, 'reduceurl').lower() != 'false'
    except:
        pass

    if reduceurl:
        uri = reduce_url(uri)
        
    return uri

def required(input, key):
    """
    Require an input parameter
    """
    val = None
    try:
        val = getattr(input, key)
    except AttributeError:
        web.ctx.status = statusmap[400]
        return "%s parameter required" % key
    return val


if __name__ == '__main__':
    application = web.application(urls, globals())
    application.run(Log)

