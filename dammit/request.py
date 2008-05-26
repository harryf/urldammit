#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, simplejson
from types import *

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
    try:
        us = simplejson.loads(s)
    except ValueError:
        logging.debug("couldnt unpack json: '%s'" % s)
        return []
    
    if not type(us) == list:
        logging.debug("not a list: '%s'" % str(us))
        return []

    return [i for i in us if is_scalar(i)]

def unpack_pairs(s):
    try:
        us = simplejson.loads(s)
    except ValueError:
        logging.debug("couldnt unpack json: '%s'" % s)
        return {}
    
    if not type(us) == dict:
        logging.debug("not a dict: '%s'" % str(us))
        return {}

    out = {}
    for k, v in us.items():
        if not is_scalar(k):
            next
        if not is_scalar(v):
            next
        out[k] = [v]

    return out

def pack_response(d):
    return simplejson.dumps(d)
