# import cherrypy
# import pytest
import requests
# import sys

from . import default


baseurl = 'http://127.0.0.1:8123/'
baseurl += 'a_setup/table/table_log/'


class TestUrl:
    """以远程访问的形式，进行HTTP接口测试，相当于外部测试，比cherrypy提供的测试方式更通用通用"""

    baseurl = baseurl
    args = "?table=tmp_users_log"

    def setup_class(self):  
        # 在开始测试之前进行的准备工作
        """没有找到直接执行数据库的方法，另外手工建测试表？"""

        print('\ninit to sqlite3 test...')
        Test = default('select')
        execute = Test.db.execute
        # db = dbapi.init('sqlite3', 'test.sqlite3', debug=True)
        # execute = db.execute
        execute("""drop table if exists tmp_users_log""")
        execute("""CREATE TABLE tmp_users_log (
            id integer primary key autoincrement ,    -- 自增主键
            did integer,       -- 数据主键，需要此字段，name才可修改，否则name不可修改
            name character varying(20),   -- 姓名
            part character varying(100),  -- 部门
            state character varying(20),  -- 状态，可能为有效，注销，挂起
            action character varying(20), -- 动作，用于显示日志，取值为：新增，修改，删除
            mtime character varying(20),  -- 修改时间
            content character varying(200)    -- 备注
            )""")

    def test_root(self):
        print('test_root:', self.baseurl + self.args)
        r = requests.get(self.baseurl + self.args)
        assert r.status_code == 200

    def test_edit(self):
        r = requests.get(self.baseurl + 'edit' + self.args)
        assert r.status_code == 200

    def test_log(self):
        r = requests.get(self.baseurl + 'log' + self.args)
        assert r.status_code == 200

    def test_insert1(self):
        """无参数插入，成功，因为有很多默认参数"""
        r = requests.get(self.baseurl + 'insert' + self.args)
        assert r.status_code == 200

    def test_insert2(self):
        """带字段值，插入成功"""
        r = requests.get(self.baseurl + 'insert' + self.args +'&name=test2')
        print('test_insert2:', r)
        dct = r.json()
        print('test_insert2:', dct)
        assert r.status_code == 200
        assert dct['did'] > 0
        assert dct['name'] == 'test2'
        assert dct['state'] == '有效'
        assert dct['mtime'] != ''
        assert dct['action'] == '增加'
        # self.test_delete2(id=dct['id'])

    def test_insert3(self):
        """带id"""

        r = requests.get(self.baseurl + 'insert' + self.args + '&id=100')
        dct = r.json()
        assert r.status_code == 200
        assert dct['id'] == 100

    def test_insert4(self):
        """带id"""

        r = requests.get(self.baseurl + 'insert' + self.args + '&did=2&name=id2&part=scb')
        dct = r.json()
        assert r.status_code == 200
        # assert dct['id'] == 100

    def test_select(self):
        """不带任何参数的默认select，排序字段，条件查找字段，错误字段名称选择、排序、查找，分页测试"""
        r = requests.get(self.baseurl + 'select' + self.args)
        assert r.status_code == 200

    def test_select1(self):
        """不带任何参数的默认查询"""
        r = requests.get(self.baseurl + 'select' + self.args)
        assert r.status_code == 200

    def test_select2(self):
        """分页参数查询"""
        r = requests.get(self.baseurl + 'select' + self.args + '&page=2&rows=10')
        assert r.status_code == 200

    def test_select3(self):
        """排序查询"""
        r = requests.get(self.baseurl + 'select' + self.args + '&sort=id&order=desc')
        assert r.status_code == 200

    def test_select4(self):
        """多字段排序查询"""
        r = requests.get(self.baseurl + 'select' + self.args + '&sort=name,id&order=desc,asc')
        assert r.status_code == 200

    def test_select5(self):
        """按字段查询条件"""
        r = requests.get(self.baseurl + 'select' + self.args + '&name=cfg_table')
        assert r.status_code == 200


    ##  还应测试穿越情况下的记录，是否显示正确。    

    def test_update1(self):
        """不带参数修改会报错"""
        r = requests.get(self.baseurl + 'update' + self.args)
        assert r.status_code == 500

    def test_update2(self):
        """修改会生成新的记录"""
        r = requests.get(self.baseurl + 'update' + self.args + '&id=1&name=update2')
        assert r.status_code == 200
        assert r.json()['id'] != 1

    def test_delete1(self):
        """不带id删除，报错"""
        r = requests.get(self.baseurl + 'delete' + self.args)
        assert r.status_code == 500

    def test_delete2(self, id=1):
        """带id删除会生成新的记录"""
        r = requests.get(self.baseurl + 'delete' + self.args + '&id=%s' % id)
        assert r.status_code == 200
        assert r.json()['success'] is True
        assert r.json()['newid'] > id
