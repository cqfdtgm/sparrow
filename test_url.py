# import cherrypy
# import os
# import os.path
# import pytest
import requests
# import sys

# from cherrypy.test import helper


baseurl = 'http://136.21.225.176:8123/'


class TestUrl:
    """以远程访问的形式，进行HTTP接口测试，相当于外部测试，比cherrypy提供的测试方式更通用通用"""

    baseurl = baseurl

    def test_root(self):
        r = requests.get(self.baseurl)
        assert r.status_code == 200

    def test_debug(self):
        r = requests.get(self.baseurl + 'debug')
        assert r.status_code == 200

    def test_users(self):
        r = requests.get(self.baseurl + 'users')
        assert r.status_code == 200

    def test_login(self):
        r = requests.get(self.baseurl + 'login')
        assert r.status_code == 200

    def test_select(self):
        r = requests.get(self.baseurl + 'select')
        assert r.status_code == 200

    def test_log(self):
        r = requests.get(self.baseurl + 'log')
        assert r.status_code == 200
