# -*- coding: utf-8 -*-
import web
web.webapi.internalerror = web.debugerror
middleware = [web.reloader]
cache = False

# couchdb database url
DBURL = 'http://localhost:5984/urldammit'
KNOWN_CACHE_SIZE = 1000
UNKNOWN_CACHE_SIZE = 100
