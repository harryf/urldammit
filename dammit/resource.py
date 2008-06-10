#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from couchdb.schema import *
from datetime import datetime
from dammit.couchutils import *
from dammit.couchutils import uri_to_id
import logging

alphanum = re.compile('^[a-zA-Z0-9]$')

class URI(Document):
    """
    Representing a URI we want urldammit to store
    """
    id = TextField()
    uri = TextField()
    location = TextField()
    status = IntegerField()
    created = DateTimeField(default=datetime.now)
    updated = DateTimeField(default=datetime.now)
    #accessed = DateTimeField(default=datetime.now)
    tags = ListField(TextField())
    pairs = ListField(DictField(
        Schema.build(k = TextField(), v = TextField())))


def equal(a, b):
    """
    equality to handle quirks of python-couchdb Document
    objects
    """
    logging.debug("Comparing %s with %s" % ( a, b ))
    if type(a) == list:
        return tuple(sorted(a)) == tuple(sorted(b))
    if type(a) == dict:
        return tuple([(k, a[k]) for k in sorted(a.keys())])\
               == tuple([(k, b[k]) for k in sorted(b.keys())])
    return a == b

def expand_dict(d):
    items = []

    if not type(d) == dict:
        return items
    
    for k, v in d.items():
        items.append({'k':k, 'v':v})

    logging.debug("expanded dict - before '%s', after '%s'" % ( d, items ))
    return items

def register_uri(db, uri, status = 200, **kwargs):
    """
    Conditionally registers a resource - updates existing
    if it's been changed
    """
    id = uri_to_id(uri)
    r = URI.load(db, id)

    logging.debug("Looking for doc with id %s [%s]" % ( id, uri ))
    
    if r:
        logging.debug("Found it")

        # once it's status is in this range, it becomes
        # immutable
        if 300 <= r.status < 400:
            logging.debug("Redirect (immutable)")
            return r
        
        kwargs['status'] = status

        if kwargs.has_key('pairs'):
            kwargs['pairs'] = expand_dict(kwargs['pairs'])
        now = datetime.now()
        updated = False

        ignore = ()
        if 400 <= status < 500:
            ignore = ('tags','pairs')

        logging.debug(ignore)
        for k, v in kwargs.items():
            logging.debug("k: %s, v: %s" % ( k, v) )
            if k in ignore:
                logging.debug("ignoring %s", k)
                continue
            
            try:
                if not equal(v, getattr(r, k)):
                    setattr(r, k, v)
                    r.updated = now
                    updated = True
            except AttributeError:
                pass

        # Too expensive write to couch on every access
        # r.accessed = now
        
        if updated:
            logging.debug("Storing changes")
            r.store(db)
        
    else:
        if 200 <= status < 300:
            logging.debug("Not found - storing")
            if kwargs.has_key('pairs'):
                kwargs['pairs'] = expand_dict(kwargs['pairs'])    
            r = URI(id = id, uri = uri, status = status, **kwargs)
            put(db, r)
        else:
            logging.debug("Not found but status is %s - ignoring" % status)

    return r
