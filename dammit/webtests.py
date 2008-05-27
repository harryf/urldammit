#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, httplib2

def run(url = "http://localhost:8080"):
    http = httplib2.Http()
    
    response, content = http.request(url, 'GET')
    assert response['status'] == '200'
    assert "where's my url dammit?" in content

    response, content = http.request("%s/test1234" % url, 'GET')
    assert response['status'] == '404'
    
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    body = {
        'uri': 'http://foobar.com/1.html',
        'status': '200',
        }

    http = httplib2.Http()
    http.follow_redirects = False
    response, content = http.request(
        url, 'POST', headers=headers, body=urllib.urlencode(body)
        )
    assert response['status'] == '303'
    assert 'http://foobar.com/1.html' in content

    http = httplib2.Http()
    response, content = http.request(
        url, 'POST', headers=headers, body=urllib.urlencode(body)
        )
    assert response['status'] == '200'
    assert 'http://foobar.com/1.html' in content

    http = httplib2.Http()
    body['tags'] = '["foo","bar"]'
    body['uri'] = 'http://foobar.com/2.html'
    response, content = http.request(
        url, 'POST', headers=headers, body=urllib.urlencode(body)
        )
    assert response['status'] == '200'
    print content
    assert '["foo", "bar"]' in content

    http = httplib2.Http()
    body['tags'] = '["abc","xyz"]'
    body['uri'] = 'http://foobar.com/2.html'
    response, content = http.request(
        url, 'POST', headers=headers, body=urllib.urlencode(body)
        )
    assert response['status'] == '200'
    assert '["abc", "xyz"]' in content

    http = httplib2.Http()
    response, content = http.request(url, 'DELETE')
    print response

    
    
    
    
    
    
