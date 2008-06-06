#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, httplib2, unittest

class WebTests(unittest.TestCase):

    def setUp(self):
        self.http = httplib2.Http()
        self.url = 'http://localhost:8080'
        self.headers = {'Content-type': 'application/x-www-form-urlencoded'}
        self.body = {
            'uri': 'http://foobar.com/1.html',
            'status': '200',
            }

    
    def testHome(self):
        response, content = self.http.request(self.url, 'GET')
        self.assert_( response['status'] == '200' )
        self.assert_("where's my url dammit?" in content)


    def test404(self):
        response, content = self.http.request("%s/test1234" % self.url, 'GET')
        self.assert_(response['status'] == '404')

    def _post(self):
        return self.http.request(
            self.url, 'POST',
            headers=self.headers,
            body=urllib.urlencode(self.body)
            )

    def test303(self):
        """
        test the direct response to a POST, without following
        the redirect
        """
        self.http.follow_redirects = False
        response, content = self._post()
        self.assert_( response['status'] == '303' )
        self.assert_( self.body['uri'] in content )


    def testPOST(self):
        response, content = self._post()
        self.assert_(response['status'] == '200')
        self.assert_( self.body['uri'] in content )

    def testTags(self):
        self.body['tags'] = '["foo","bar"]'
        self.body['uri'] = 'http://foobar.com/2.html'
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )        
        self.assert_( '["foo", "bar"]' in content )

    def testMoreTags(self):
        self.body['tags'] = '["abc","xyz"]'
        self.body['uri'] = 'http://foobar.com/2.html'
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )
        self.assert_( '["abc", "xyz"]' in content )

    def testDELETE(self):
        self.body['uri'] = 'http://foobar.com/deleteme.html'
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )
        response, content = self.http.request(
            response['content-location'], 'DELETE'
            )
        self.assert_( response['status'] == '204' )

if __name__ == '__main__':
    unittest.main()
    
    
