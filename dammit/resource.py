#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from couchdb.schema import *
from datetime import datetime
from dammit.couchutils import *

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
    accessed = DateTimeField(default=datetime.now)
    tags = ListField(TextField())
    pairs = ListField(
        DictField(
        Schema.build(key = TextField(), value = TextField()))
        )

def register_uri(db, uri, status = 200, **kwargs):
    """
    Conditionally registers a resource - updates existing
    if it's been changed
    """
    id = uri_to_id(uri)
    r = URI.load(db, id)
    
    if r:
        kwargs['status'] = status
        now = datetime.now()
        updated = False
        
        for k, v in kwargs.items():
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
            r.store(db)
        
    else:
        r = URI(id = id, uri = uri, status = status, **kwargs)
        put(db, r)

    return r
