#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, httplib2, unittest, sys

class WebTests(unittest.TestCase):

    def setUp(self):
        self._init_http()
        self.url = 'http://localhost:8080'
        self.headers = {'Content-type': 'application/x-www-form-urlencoded'}
        self.body = {
            'uri': 'http://foobar.com/setup.html',
            'status': '200',
            }

    def _init_http(self):
        self.http = httplib2.Http()
        
    def _post(self):
        return self.http.request(
            self.url, 'POST',
            headers=self.headers,
            body=urllib.urlencode(self.body)
            )

    def testHome(self):
        response, content = self.http.request(self.url, 'GET')
        self.assert_( response['status'] == '200' )
        self.assert_("where's my url dammit?" in content)


    def test404(self):
        self.body['uri'] = 'http://foobar.com/%s.html'\
                           % sys._getframe().f_code.co_name
        response, content = self.http.request(
            "%s/test1234" % self.url, 'GET'
            )
        self.assert_(response['status'] == '404')


    def test303(self):
        # test the direct response to a POST
        # without following the redirect
        self.body['uri'] = 'http://foobar.com/%s.html'\
                           % sys._getframe().f_code.co_name
        self.http.follow_redirects = False
        response, content = self._post()
        self.assert_( response['status'] == '303' )
        self.assert_( self.body['uri'] in content )


    def testPOST(self):
        # TODO test updated time
        self.body['uri'] = 'http://foobar.com/%s.html'\
                           % sys._getframe().f_code.co_name
        response, content = self._post()
        self.assert_(response['status'] == '200')
        self.assert_( self.body['uri'] in content )

    def testTags(self):
        # TODO test updated time
        self.body['uri'] = 'http://foobar.com/%s.html'\
                           % sys._getframe().f_code.co_name
        self.body['tags'] = '["foo","bar"]'
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )        
        self.assert_( '["foo", "bar"]' in content )

    def testTagChange(self):
        # TODO test updated time!
        self.body['uri'] = 'http://foobar.com/%s.html'\
                           % sys._getframe().f_code.co_name
        
        self.body['tags'] = '["foo","bar"]'
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )        
        self.assert_( '["foo", "bar"]' in content )

        self._init_http()
        self.body['tags'] = '["abc","xyz"]'
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )
        self.assert_( '["abc", "xyz"]' in content )
    
    def testDELETE(self):
        self.body['uri'] = 'http://foobar.com/%s.html'\
                        % sys._getframe().f_code.co_name
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )

        uri = response['content-location']
        
        self._init_http()
        response, content = self.http.request(
            uri, 'DELETE'
            )

        self.assert_( response['status'] == '204' )

        self._init_http()
        response, content = self.http.request(
            uri, 'GET'
            )
        self.assert_( response['status'] == '404' )

    def testDeleteViaPost(self):
        # with empty value in status field, record is deleted
        self.body['uri'] = 'http://foobar.com/%s.html'\
                        % sys._getframe().f_code.co_name        
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )

        uri = response['content-location']
        
        self._init_http()
        self.body['status'] = ''
        response, content = self._post()
        self.assert_( response['status'] == '204' )
        
        self._init_http()
        response, content = self.http.request(
            uri, 'GET'
            )
        self.assert_( response['status'] == '404' )

    def testHEAD(self):
        self.body['uri'] = 'http://foobar.com/%s.html'\
                        % sys._getframe().f_code.co_name
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )
        
        self._init_http()
        response, content = self.http.request(
            response['content-location'], 'HEAD'
            )
        self.assert_( response['status'] == '200' )
        self.assert_( content.strip() == '' )

    def testBadrequest(self):
        self.body['uri'] = 'http://foobar.com/%s.html'\
                        % sys._getframe().f_code.co_name
        self.body['status'] = 'abc'
        response, content = self._post()
        self.assert_( response['status'] == '400' )
    

if __name__ == '__main__':
    unittest.main()
    
    
