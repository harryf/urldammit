#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime, re, logging
from types import *
from urlparse import urlsplit, urlunsplit
from urllib import unquote_plus as urldecode
import simplejson

def is_scalar(i):
    """
    >>> is_scalar('Foo')
    True
    >>> is_scalar([1,2])
    False
    """
    scalars = (NoneType, BooleanType, IntType, LongType,
               FloatType, ComplexType, StringType,
               UnicodeType)

    if type(i) in scalars:
        return True

    return False

def unpack_tags(s):
    """
    >>> unpack_tags(None)
    >>> unpack_tags('')
    >>> unpack_tags('foobar')
    >>> [u'x', 1] == unpack_tags('["x", 1]')
    True
    >>> [u'x', 1] == unpack_tags('["x", 1, {"y": 2}]')
    True
    """
    if not s or s == '':
        return None
    try:
        us = simplejson.loads(s)
    except ValueError, e:
        return None

    if not type(us) == list:
        return None

    return [i for i in us if is_scalar(i)]

non_ascii_pattern = re.compile('[^\x09\x0A\x0D\x20-\x7E]+')
def decode_string(s):
    """
    >>> decode_string('foo')
    u'foo'
    >>> decode_string('foo%20bar')
    u'foo bar'
    >>> decode_string('föö%20bär')
    u'f\\xf6\\xf6 b\\xe4r'
    """
    try:
        s = s.decode('utf-8')
    except:
        s = unicode(non_ascii_pattern.sub('', s))
    return urldecode(s)
    
def unpack_pairs(s):
    """
    >>> unpack_pairs(None)
    >>> unpack_pairs('')
    >>> unpack_pairs('foobar')
    >>> {u'y':2} == unpack_pairs('{"y": 2}')
    True
    >>> {u'y':2} == unpack_pairs('{"y": 2, "x":[1,2]}')
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
        try:
            out[decode_string(k)] = decode_string(v)
        except:
            out[k] = v

    return out

def pack_response(u):
    """
    Construct an response as JSON
    >>> pack_response('')
    '{}'
    >>> class TestUri: uri = 'http://www.google.com'
    >>> pack_response(TestUri())
    '{"uri": "http://www.google.com"}'
    >>> class TestUri: status = 200
    >>> pack_response(TestUri())
    '{"status": "200"}'
    >>> class TestUri: created = datetime.datetime(2009,1,1)
    >>> pack_response(TestUri())
    '{"created": "2009-01-01 00:00:00"}'
    >>> class TestUri: updated = datetime.datetime(2009,1,1)
    >>> pack_response(TestUri())
    '{"updated": "2009-01-01 00:00:00"}'
    >>> class TestUri: location = 'http://www.google.com'
    >>> pack_response(TestUri())
    '{"location": "http://www.google.com"}'
    >>> class TestUri: tags = ['foo','bar']
    >>> pack_response(TestUri())
    '{"tags": ["foo", "bar"]}'
    >>> class TestUri: pairs = {'foo':'bar'}
    >>> pack_response(TestUri())
    '{"pairs": {"foo": "bar"}}'
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
    403: '403 Forbidden',
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
