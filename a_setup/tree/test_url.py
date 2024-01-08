# import cherrypy
# import os.path
# import pytest
import requests
# import sys

# from cherrypy.test import helper

from ... import dbapi
from ... import private
# from .. import default

baseurl = 'http://127.0.0.1:8123/'
baseurl += 'a_setup/tree/'


class TestUrl:
    """以远程访问的形式，进行HTTP接口测试，相当于外部测试，比cherrypy提供的测试方式更通用通用
    对于tree应用来说，需要测试以下：查询，新增，删除，更改，移动"""

    # db = default.db

    def setup_class(self):
        """重新创建测试表 test_org"""

        print('是每运行一个测试，就要运行一次本函数？')
        self.baseurl = baseurl
        self.db = dbapi.init(*private.conn_sqlite_1)
        self.db.execute("drop table if exists test_org")
        self.db.execute("""create table test_org (id integer primary key autoincrement NOT NULL
        , text varchar(200), 
        parentid integer not null, state varchar(20), display integer) """)
        self.db.commit()

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
        """无参数插入，默认根节点"""
        r = requests.get(self.baseurl + 'insert?table=test_org&parentId=0')
        dct = r.json()
        print('dct:', dct)
        assert r.status_code == 200

    def test_insert2(self):
        """播放共4个记录，tree返回的会是无total的列表"""
        requests.get(self.baseurl + 'insert?table=test_org&parentId=0')
        requests.get(self.baseurl + 'insert?table=test_org&parentId=0')
        r = requests.get(self.baseurl + 'insert?table=test_org&parentId=0')
        dct = r.json()
        print('dct:', dct)
        assert r.status_code == 200
        assert dct['id'] == 4
        assert dct['text'] == 'New Item'
        assert dct['state'] == 'open'
        assert dct['parentid'] == 0
        r = requests.get(self.baseurl + 'tree?table=test_org')
        assert r.status_code == 200
        dct = r.json()
        assert len(dct) == 4
        print('dct: in 4', dct)

    def test_insert3(self):
        """下级数量限制，和翻页参数"""
        for _ in range(6):
            requests.get(self.baseurl + 'insert?table=test_org&parentId=0')
        r = requests.get(self.baseurl + 'insert?table=test_org&parentId=0')   # 第11条插入会失败
        dct = r.json()
        print('dct insert 11', dct)
        assert dct['isError'] is True
        r = requests.get(self.baseurl + 'tree?table=test_org')
        assert r.status_code == 200
        dct = r.json()
        assert dct['total'] == 10
        assert dct['rows'][3]['id'] == 4
        print('dct of page:', dct)
        r = requests.get(self.baseurl + 'tree?page=3&table=test_org')
        assert r.status_code == 200
        dct = r.json()
        assert dct['total'] == 10
        assert dct['rows'][0]['id'] == 9
        print('dct of page:', dct)

    def test_insert_children(self):
        """第11－20条记录插入到1的下级"""
        for _ in range(10):
            requests.get(self.baseurl + 'insert?table=test_org&parentId=1')
        r = requests.get(self.baseurl + 'tree?table=test_org&parentId=1&page=2')
        assert r.status_code == 200

    def test_dnd1(self):
        """拖拽测试，分为append, button, top"""

        # 将11拖到10之后，会因数量限制失败
        r = requests.get(self.baseurl + 'dnd?table=test_org&id=11&targetid=10&point=buttom')
        dct = r.json()
        assert dct['isError'] is True, "根目录已满"
        r = requests.get(self.baseurl + 'dnd?table=test_org&id=10&targetid=1&point=append')
        dct = r.json()
        assert dct['isError'] is True, "节点1下级已满"
        r = requests.get(self.baseurl + 'dnd?table=test_org&id=10&targetid=11&point=top')
        dct = r.json()
        assert dct['isError'] is True, "节点1下级已满"

    def test_dnd2(self):
        """同级拖动，改变显示顺序"""

        r = requests.get(self.baseurl + 'dnd?table=test_org&id=12&targetid=14&point=top')
        dct = r.json()
        assert dct['success'] is True, "将12拖到14前面"
        r = requests.get(self.baseurl + 'dnd?table=test_org&id=11&targetid=13&point=button')
        dct = r.json()
        assert dct['success'] is True, "将11拖到13后面"
        requests.get(self.baseurl + 'delete?table=test_org&id=20')
        r = requests.get(self.baseurl + 'dnd?table=test_org&id=15&targetid=1&point=append')
        dct = r.json()
        assert dct['success'] is True, "将15拖到1下面（追加，会放在最后）"
        dct = requests.get(self.baseurl + 'tree?page=1&table=test_org&id=1').json()
        assert [item['id'] for item in dct['rows']] == [13, 11, 12, 14]
        dct = requests.get(self.baseurl + 'tree?page=2&table=test_org&id=1').json()
        assert [item['id'] for item in dct['rows']] == [16, 17, 18, 19]
        dct = requests.get(self.baseurl + 'tree?page=3&table=test_org&id=1').json()
        assert [item['id'] for item in dct['rows']] == [15]

    def test_dnd3(self):
        """拖动到其他节点下级，显示顺序会是最后一个；拖动到其他父节点下的某个子节点后面或前面，显示顺序会在其之后或之前"""
        requests.get(self.baseurl + 'dnd?table=test_org&id=3&targetid=2&point=append')
        requests.get(self.baseurl + 'dnd?table=test_org&id=4&targetid=2&point=append')
        requests.get(self.baseurl + 'dnd?table=test_org&id=5&targetid=4&point=top')
        requests.get(self.baseurl + 'dnd?table=test_org&id=6&targetid=4&point=buttom')
        dct = requests.get(self.baseurl + 'tree?page=1&table=test_org&id=2').json()
        print('dct: dnd3', dct)
        assert [item['id'] for item in dct] == [3, 5, 4, 6]

    def test_tree(self):
        """不带任何参数的默认tree，排序字段，条件查找字段，错误字段名称选择、排序、查找，分页测试"""
        r = requests.get(self.baseurl + 'tree?table=test_org')
        assert r.status_code == 200

    def test_tree1(self):
        """不带任何参数的默认查询"""
        r = requests.get(self.baseurl + 'tree?table=test_org')
        assert r.status_code == 200

    def test_update1(self):
        r = requests.get(self.baseurl + 'update?table=test_org')
        assert r.status_code == 500, "不带id的更新会失败"
        r = requests.get(self.baseurl + 'update?table=test_org&id=2&text=name2')
        assert r.status_code == 200
        dct = requests.get(self.baseurl + 'tree?page=1&table=test_org&id=0').json()
        assert [item['text'] for item in dct['rows']] == ['New Item', 'name2', 'New Item', 'New Item']

    def test_delete2(self, id=1):
        """带id"""
        r = requests.get(self.baseurl + 'delete?id=%s&table=test_org' % id)
        assert r.status_code == 200
        assert r.json()['isError'] is True, "必须先删除下级节点"

    def test_delete3(self, id=9):
        """带id"""
        r = requests.get(self.baseurl + 'delete?id=%s&table=test_org' % id)
        assert r.status_code == 200
        assert r.json()['success'] is True, "删除节点成功"
