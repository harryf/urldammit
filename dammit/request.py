#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from urlparse import urlsplit, urlunsplit
from types import *
import simplejson
import datetime

def is_scalar(i):
    scalars = (NoneType, BooleanType, IntType, LongType,
               FloatType, ComplexType, StringType,
               UnicodeType)

    if type(i) in scalars:
        return True

    return False

def is_pair(i):
    # todo check it's a key value pair
    return True

def unpack_tags(s):
    """
    >>> unpack_tags(None)
    >>> unpack_tags('')
    >>> unpack_tags('foobar')
    >>> ["x", "1"] == unpack_tags('["x", 1]')
    True
    >>> ["x", "1"] == unpack_tags('["x", 1, {"y": 2}]')
    True
    """
    if not s or s == '':
        return None
    try:
        us = simplejson.loads(s)
    except ValueError:
        return None
    
    if not type(us) == list:
        return None

    return [str(i) for i in us if is_scalar(i)]

def unpack_pairs(s):
    """
    >>> unpack_pairs(None)
    >>> unpack_pairs('')
    >>> unpack_pairs('foobar')
    >>> {"y":"2"} == unpack_pairs('{"y": 2}')
    True
    >>> {"y":"2"} == unpack_pairs('{"y": 2, "x":[1,2]}')
    True
    """
    if not s or s == '':
        return None
    
    try:
        us = simplejson.loads(s)
    except ValueError:
        return None
    
    if not type(us) == dict:
        return None

    out = {}
    for k, v in us.items():
        if not is_scalar(k) or not is_scalar(v):
            continue
        out[str(k)] = str(v)

    return out

def pack_response(u):
    """
    Construct an response as JSON
    """
    keys = ('uri','status','created','updated',
            'location','tags','pairs')

    d = {}
    for key in keys:
        try:
            v = getattr(u, key)
            if is_scalar(v) or type(v) == datetime.datetime:
                d[key] = str(v)
            else:
                d[key] = v
        except:
            pass

    try:
        return simplejson.dumps(d)
    except:
        logging.error("Can't dump '%s'" % d)
        return ''

statusmap = {
    200: '200 OK',
    201: '201 Created',
    202: '202 Accepted',
    204: '204 No Content',
    300: '300 Multiple Choices',
    301: '301 Moved Permanently',
    302: '302 Found',
    303: '303 See Other',
    304: '304 Not Modified',
    305: '305 Use Proxy',
    306: '305 Switch Proxy',
    307: '307 Temporary Redirect',
    400: '400 Bad Request',
    404: '404 Not Found',
    }

def reduce_url(url):
    """
    for a URL like http://example.com/page.html?foo=bar
    we only want the 'http://example.com/page.html'
    by default

    >>> print reduce_url('http://example.com/page.html?foo=bar')
    http://example.com/page.html
    >>> print reduce_url('http://example.com/')
    http://example.com/
    >>> print reduce_url('http://example.com')
    http://example.com
    """
    return urlunsplit(urlsplit(url)[0:3]+('',''))

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
