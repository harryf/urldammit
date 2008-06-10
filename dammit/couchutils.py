#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sha

class InvalidID(Exception):
    pass

def put(database, document):
    """
    couchdb-python schemas only support use of IDs generated
    by couchdb - need to explicitly PUT the doc
    """
    if not document.id:
        raise InvalidID()

    data = dict([(k, v) for k, v in document._data.items()
                 if (k not in ('id') and not k.startswith('_'))])

    database.resource.put(document.id, content = data)

def delete(database, id, rev):
    """
    delete a doc from the db
    """
    database.resource.delete(id, rev)

def uri_to_id(uri):
    """
    SHA-1 the URI's so couchdb can handle them
    """
    return sha.new(uri).hexdigest()
