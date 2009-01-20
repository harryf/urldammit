#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, httplib2, unittest, sys, datetime

REPORT = False

def Report(test):
    def runtest(self):
        if not test.__name__ == 'test303':
            return
        if REPORT: print "[%s] testing %s" % ( datetime.datetime.now(), test.__name__ )
        test(self)
        if REPORT: print "[%s] testing %s done" % ( datetime.datetime.now(), test.__name__ )
    return runtest


class WebTests(unittest.TestCase):

    def setUp(self):
        self.http = None
        self._init_http()
        self.url = 'http://localhost:8080'
        self.headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Connection': 'Close',
            }
        self.body = {
            'uri': 'http://foobar.com/setup.html',
            'status': '200',
            }

    def tearDown(self):
        if self.http: del self.http
            
    def _init_http(self):
        if self.http: del self.http
        self.http = httplib2.Http(timeout = 10)
        
    def _post(self):
        return self.http.request(
            self.url, 'POST',
            headers=self.headers,
            body=urllib.urlencode(self.body)
            )

    @Report
    def testHome(self):
        response, content = self.http.request(self.url, 'GET')
        self.assert_( response['status'] == '200' )
        self.assert_("where's my url dammit?" in content)

    @Report
    def test404(self):
        self.body['uri'] = 'http://foobar.com/%s.html'\
                           % sys._getframe().f_code.co_name
        response, content = self.http.request(
            "%s/test1234" % self.url, 'GET'
            )
        self.assert_(response['status'] == '404')

    @Report
    def test303(self):
        # test the direct response to a POST
        # without following the redirect
        self.body['uri'] = 'http://foobar.com/%s.html'\
                           % sys._getframe().f_code.co_name
        self.http.follow_redirects = False
        response, content = self._post()
        self.assert_( response['status'] == '303' )
        self.assert_( content == 'None' )


    @Report
    def testPOST(self):
        # TODO test updated time
        self.body['uri'] = 'http://foobar.com/%s.html'\
                           % sys._getframe().f_code.co_name
        response, content = self._post()
        self.assert_(response['status'] == '200')
        self.assert_( self.body['uri'] in content )

    @Report
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

    @Report
    def testDeleteViaPost(self):
        # with empty value in status field, record is deleted
        self.body['uri'] = 'http://foobar.com/%s.html'\
                        % sys._getframe().f_code.co_name
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )
        
        uri = response['content-location']
        
        self._init_http()
        self.body['delete'] = 'true'
        response, content = self._post()
        self.assert_( response['status'] == '204' )

        self._init_http()
        response, content = self.http.request(
            uri, 'GET'
            )
        self.assert_( response['status'] == '404' )

    @Report
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

    @Report
    def testPUT(self):
        self.body['uri'] = 'http://foobar.com/%s.html'\
                        % sys._getframe().f_code.co_name
        response, content = self._post()
        print response
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )
        
        uri = response['content-location']

        self._init_http()
        self.body['status'] = '404'
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( '404' in content )

        self._init_http()
        self.body['status'] = '301'
        self.body['location'] = 'http://local.ch/foobar.html'
        response, content = self._post()

        print response
        print "c: " + content
        self.assert_( response['status'] == '200' )
        self.assert_( '301' in content )
        self.assert_( self.body['location'] in content )

        self._init_http()
        self.body['status'] = '200'
        self.body['location'] = None
        response, content = self.http.request(
            uri, 'PUT',
            headers=self.headers,
            body=urllib.urlencode(self.body)
            )
        print response
        self.assert_( response['status'] == '200' )
        self.assert_( content.strip() == '' )


    @Report
    def testBadrequest(self):
        self.body['uri'] = 'http://foobar.com/%s.html'\
                        % sys._getframe().f_code.co_name
        self.body['status'] = 'abc'
        response, content = self._post()
        self.assert_( response['status'] == '400' )

    @Report
    def testTags(self):
        # TODO test updated time
        self.body['uri'] = 'http://foobar.com/%s.html'\
                           % sys._getframe().f_code.co_name
        self.body['tags'] = '["foo","bar"]'
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )        
        self.assert_( '["foo", "bar"]' in content )

    @Report
    def testPairs(self):
        self._init_http()
        # TODO test updated time
        self.body['uri'] = 'http://foobar.com/%s.html'\
                           % sys._getframe().f_code.co_name
        self.body['pairs'] = '{"x":1, "y" : 2}'
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( self.body['uri'] in content )
        self.assert_( '"y": "2"' in content )
        self.assert_( '"x": "1"' in content )

    @Report
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

    def testReduceURL(self):
        self.body['uri'] = 'http://foobar.com/%s.html?foo=bar'\
                           % sys._getframe().f_code.co_name
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( 'foo=bar' not in content )

        self._init_http()
        self.body['uri'] = 'http://foobar.com/%s_2.html?abc=xyz'\
                           % sys._getframe().f_code.co_name
        self.body['reduceurl'] = 'false'
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( 'abc=xyz' in content )

    def testFind(self):
        from urllib2 import quote
        self.body['uri'] = 'http://foobar.com/%s.html?foo=bar'\
                           % sys._getframe().f_code.co_name
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( 'foo=bar' not in content )
        
        uri = response['content-location']

        self._init_http()
        findurl = 'http://localhost:8080/find/%s' % quote(self.body['uri'])
        response, content = self.http.request(
            findurl, 'GET'
            )
        self.assert_( response['content-location'] == uri)

        self._init_http()
        self.body['uri'] = 'http://foobar.com/%s.html?foo=bar'\
                           % sys._getframe().f_code.co_name
        self.body['reduceurl'] = 'false'
        response, content = self._post()
        self.assert_( response['status'] == '200' )
        self.assert_( 'foo=bar' in content )

        uri = response['content-location']

        self._init_http()
        findurl = 'http://localhost:8080/find/%s?reduceurl=false' % quote(self.body['uri'])
        response, content = self.http.request(
            findurl, 'GET'
            )
        self.assert_( response['content-location'] == uri)




if __name__ == '__main__':
    unittest.main()
    
    
