# import cherrypy
# import os
# import os.path
# import pytest
import requests
# import sys

# from cherrypy.test import helper

# from ... import dbapi
# from ... import private
from .. import default

baseurl = 'http://136.21.225.176:8123/'
baseurl += 'a_setup/tree/'


class TestUrl:
    """以远程访问的形式，进行HTTP接口测试，相当于外部测试，比cherrypy提供的测试方式更通用通用
    对于tree应用来说，需要测试以下：查询，新增，删除，更改，移动"""

    baseurl = baseurl
    # db = dbapi.init(*private.conn_pg15)
    db = default.db

    def setup_class(self):
        """重新创建测试表 test_org"""

        self.db.execute("drop table if exists test_org;")
        self.db.execute("""create table test_org (	id serial primary key , text varchar(200), 
        parentid integer not null, state varchar(20), display integer) """)

    def teardown_class(self):
        pass

    def test_root(self):
        r = requests.get(self.baseurl)
        assert r.status_code == 200

    def test_edit(self):
        r = requests.get(self.baseurl + 'edit')
        assert r.status_code == 200

    def test_log(self):
        r = requests.get(self.baseurl + 'log')
        assert r.status_code == 200

    def test_insert1(self):
        """无参数插入，报错"""
        r = requests.get(self.baseurl + 'insert')
        dct = r.json()
        print('dct:', dct)
        assert r.status_code == 200

    def test_insert2(self):
        """第4个插入会返回报错信息"""
        r = requests.get(self.baseurl + 'insert')
        r = requests.get(self.baseurl + 'insert')
        r = requests.get(self.baseurl + 'insert')
        dct = r.json()
        assert r.status_code == 200
        assert dct['kind'] == 'test'
        assert dct['name'] == 'test2'
        self.test_delete2(id=dct['id'])

    def test_insert3(self):
        """带id"""
        r = requests.get(self.baseurl + 'insert?id=100')
        dct = r.json()
        assert r.status_code == 200
        assert dct['id'] == 100
        # self.test_delete2(id=dct['id'])   # 留待后面删除

    def test_select(self):
        """不带任何参数的默认select，排序字段，条件查找字段，错误字段名称选择、排序、查找，分页测试"""
        r = requests.get(self.baseurl + 'select')
        assert r.status_code == 200

    def test_select1(self):
        """不带任何参数的默认查询"""
        r = requests.get(self.baseurl + 'select')
        assert r.status_code == 200

    def test_select2(self):
        """分页参数查询"""
        r = requests.get(self.baseurl + 'select?page=2&rows=10')
        assert r.status_code == 200

    def test_select3(self):
        """排序查询"""
        r = requests.get(self.baseurl + 'select?sort=id&order=desc')
        assert r.status_code == 200

    def test_select4(self):
        """多字段排序查询"""
        r = requests.get(self.baseurl + 'select?sort=name,id&order=desc,asc')
        assert r.status_code == 200

    def test_select5(self):
        """按字段查询条件"""
        r = requests.get(self.baseurl + 'select?name=cfg_table')
        assert r.status_code == 200

    def test_update1(self):
        r = requests.get(self.baseurl + 'update')
        assert r.status_code == 500

    def test_update2(self):
        r = requests.get(self.baseurl + 'update?id=100&kind=update')
        assert r.status_code == 200
        assert r.json()['kind'] == 'update'

    def test_delete1(self):
        """不带id删除，报错"""
        r = requests.get(self.baseurl + 'delete')
        assert r.status_code == 500

    def test_delete2(self, id=100):
        """带id"""
        r = requests.get(self.baseurl + 'delete?id=%s' % id)
        assert r.status_code == 200
        assert r.json()['success'] is True
