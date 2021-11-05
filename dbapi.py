# dbapi.py
# access to the database

"""
Only special CRUD to a database, map to SQL:
C-create -> insert
R-receive -> select
U-update -> update(id=?)
D-delete -> delete(id=?)
"""

import abc
# import collections
# import json
# import os
import psycopg2
import pytest
import sqlite3
# import sys
# import traceback

from . import private


def init(db_type, connect_str, _debug=True):
    """返回由db_type指定类型，connect_str指定具体连接的数据库对象
    目前本文件中定义了以下db_type及连接字符串格式:
    sqlite3, test.sqlite3
    """

    db_type = db_type.capitalize()  # 首字母大写以符合类名规范
    return globals()['Database' + db_type](connect_str, _debug=_debug)


class Database(abc.ABC):
    """A class to access database, define CRUD"""

    # 数据库类属性用下划线开头的原因，是防止与表名冲突。
    _param_style = ""
    _limit = ""
    _limit_0 = ""
    _connect = None

    def __init__(self, _connect_str, _debug=False):
        self._connect_str = _connect_str
        self._debug = _debug

    def __del__(self):
        if '_cur' in self.__dict__:
            print('db del..')
            self._cur.close()
            self._con.close()

    def __getattr__(self, _table):
        """未访问过的表，会将其字段结构取来，作为类的属性，该表用select返回的类cur对象表示"""
        if not _table.startswith('_'):
            table = self.select(_table=_table, _limit=self._limit_0)
            setattr(self.__class__, _table, table)
            return table

    @property
    def _con(self):
        """只在访问该属性才才建立连接，并设为属性，避免二次连接"""
        # print('connect @ abc..', self.connect)
        if '_con' not in self.__dict__:
            print('con:', self._connect, self._connect_str)
            self.__dict__['_con'] = self.__class__._connect(self._connect_str)
        return self.__dict__['_con']

    @property
    def _cur(self):
        """只在需要时才建立游标，并设为属性，避免二次建立 """
        if '_cur' not in self.__dict__:
            self.__dict__['_cur'] = self._con.cursor()
        return self.__dict__['_cur']

    def select(self, _table="", _columns="*", _order="", _limit="", **kw):
        """select data from database
        这些参数尽量用下划线，是为了防止与表名相冲突
        _order: 每个数据库的实现不一样
        _limit: 每个数据库的实现不一样
        kw: key is column of table, value is column's value
        """

        # self._kw = kw
        sql = "select %(_columns)s from %(_table)s %(wheres)s %(_order)s" \
              "%(_limit)s"
        wheres, values = self._where_process(**kw)
        sql = sql % locals()
        print('kw:', kw, wheres, values)
        cur = self._execute(sql, values)
        result = dict()
        result['data'] = cur.fetchall()
        result['desc'] = cur.description
        result['description'] = cur.description
        result['columns'] = [i[0].lower() for i in cur.description]
        result['rows'] = [dict(zip(result['columns'], i)) for i in result['data']]
        result['rowcount'] = len(result['data'])
        return result

    def count(self, _table="", **kw):

        kw.pop('page', None)
        kw.pop('rows', None)
        kw.pop('order', None)
        kw.pop('sort', None)
        wheres, values = self._where_process(**kw)
        sql = "select count(*) as cnt from %(_table)s %(wheres)s"
        # print('SQL @ count:', sql, locals(), kw)
        sql = sql % locals()
        cur = self._execute(sql, values)
        return cur.fetchall()[0]['cnt']

    def insert(self, _table="", **kw):
        """返回新插入的记录的id"""

        # self._kw = kw
        sql = "insert into %(_table)s (%(columns)s) values (%(values)s)"
        columns = ",".join(kw.keys())
        values = ",".join([self._param_style] * len(kw))
        sql = sql % locals()
        cur = self._execute(sql, list(kw.values()))
        return cur.lastrowid

    def delete(self, _table="", id=None):
        """返回受影响的行数"""

        sql = "delete from %(_table)s where id=%(id)s"
        sql = sql % locals()
        result = self._execute(sql, [])
        return result.rowcount

    def update(self, _table="", id=None, **kw):
        """返回更新成功的受影响的行数"""

        sql = "update %(_table)s set %(changes)s where id=%(id)s"
        changes = ",".join(" %s=%s " % (column, self._param_style)
                           for column in kw)
        sql = sql % locals()
        result = self._execute(sql, list(kw.values()))
        return result.rowcount
        # 如果更新成功，应返回该条记录的结果字典
        # if result['rowcount'] == 1:
        #    return self.select(_table=_table, id=id)['rows'][0]
        # return result['rowcount']

    def _where_process(self, **kw):
        wheres, values = ['1=1'], []
        for column, value in kw.items():
            if isinstance(value, str):
                if '%' in value:
                    wheres.append("%s like %s" % (column, self._param_style))
                    values.append(value)
                else:
                    wheres.append("%s = %s" % (column, self._param_style))
                    values.append(value)
            elif isinstance(value, int):
                wheres.append("%s = %s" % (column, self._param_style))
                values.append(value)
        wheres = " where " + " and ".join(wheres)
        """if wheres:
            wheres = " where " + ' and '.join(wheres)
        else:
            wheres = ''
            """
        return wheres, values

    '''
    @abc.abstractmethod
    def _execute(self, sql, values):
        """must be override, to return such as this
        返回一个类似cursor的对象，"""

        return
    '''


class DatabasePostgresql(Database):
    """继承自Database, 具体指定了数据库类型为postgresql"""

    _param_style = '%s'
    _limit = " limit %(rows)s offset %(page)s "
    _limit_0 = _limit % {'rows': 0, 'start': 0, 'page': 0}
    _connect = psycopg2.connect

    def select(self, rows=10, page=1, *k, **kw):
        """要重写，以便转换适用于easyui的翻页参数名称"""

        kw['_limit'] = self._limit % locals()
        return super(self.__class__, self).select(*k, **kw)

    def insert(self, _table=None, **kw):
        """覆写再调用，插入后需要执行lastval()以取得上次插入的记录id"""
        super(DatabasePostgresql, self).insert(_table, **kw)
        if 'id' in kw:
            return kw['id']
        else:
            lastrowid = self._execute("select lastval() as id").fetchall()[0][0]
            return lastrowid

    def _commit(self):
        self._con.commit()

    def _rollback(self):
        self._con.rollback()

    def _begin(self):
        self._con.commit()
        self._con.autocommit = True

    def _execute(self, sql, values=()):
        """使用本类中初始化的con, cur来执行SQL语句，并返回结果。
        本方法并不进行事务方面的处理，事务由本方法的调用者处理
        """

        if self._debug:
            print(self._debug, 'SQL @ _execute: ', sql, values, self.__class__.__name__)
        cur = self._cur
        cur.execute(sql, values)
        return cur


class DatabaseSqlite3(Database):

    _param_style = '?'
    _limit = " limit %(start)s, %(rows)s "
    _limit_0 = _limit % {'rows': 0, 'start': 0, 'page': 0}
    _connect = sqlite3.connect

    def select(self, rows=10, page=1, *k, **kw):
        """要重写，以便转换适用于easyui的翻页参数名称"""

        start = (int(page)-1) * int(rows)
        kw['_limit'] = self._limit % locals()
        return super(self.__class__, self).select(*k, **kw)

    def _execute(self, sql, values=()):
        """使用本类中初始化的con, cur来执行SQL语句，并返回结果。
        本方法并不进行事务方面的处理，事务由本方法的调用者处理
        """

        if self._debug:
            print('SQL @ _execute: ', sql, values)
        cur = self._cur
        cur.execute(sql, values)
        return cur


# 本文件与框架无关，所以可能单独进行单元测试
# 测试方式： pytest dbapi.py

def test_not_exists_dbtype():
    """空的或错误的数据库类型会引发keyError错误，因为本文件全局变量中没有Database_xx这个数据库类型"""

    with pytest.raises(KeyError):
        init('hasno', '')


def test_not_instance():
    """测试：抽象基类不能直接实例化"""

    with pytest.raises(TypeError):
        Database('')


class CommTest(abc.ABC):
    """公共测试基类，不实际测试，所以不能以Test开头"""

    db = None

    @abc.abstractmethod
    def setup_class(self):
        # self.db = None
        pass

    @abc.abstractmethod
    def teardown_class(self):
        pass

    def test_insert(self):
        new_id = self.db.insert(_table='tmp_users', name='name1', age=1, price=1.1)
        print('new_id, ', self.__class__.__name__, new_id)
        assert new_id == 1
        # 指定id的插入，pg不能返回正确的lastrowid, sqlite是可以的
        new_id = self.db.insert(id=7, _table='tmp_users', name='name2', age=2, price=2.1)
        assert new_id == 7
        new_id = self.db.insert(id=5, _table='tmp_users', name='name3', age=3, price=3.1)
        assert new_id == 5

    def test_select_one(self):
        rec = self.db.select(_table='tmp_users', id=1)
        print('rec @ test_select_one:', self.__class__.__name__, rec)
        assert rec['rowcount'] == 1
        assert rec['columns'] == ['id', 'name', 'age', 'price']
        assert rec['rows'][0]['id'] == 1
        assert rec['rows'][0]['name'] == 'name1'
        # print(dir(row['price']))
        # print('%s' % row['price'], float(row['price']))
        assert float(rec['rows'][0]['price']) == 1.1

    def test_select_multi(self):
        rec = self.db.select(_table='tmp_users', _order='order by id desc')
        assert len(rec['rows']) == 3
        rows = rec['rows']
        assert rows[0]['id'] == 7
        assert rows[1]['id'] == 5
        assert rows[2]['id'] == 1
        rec = self.db.select(_table='tmp_users', name='%e2%', _order='order by id desc')
        assert len(rec['rows']) == 1
        assert rec['rows'][0]['id'] == 7

    def test_update(self):
        rec = self.db.update(_table='tmp_users', id=1, name='name11', price=12.1)
        print('update of sqlite:', rec)
        assert rec == 1
        rec = self.db.select(_table='tmp_users', id=1, _columns="id,name,price")
        assert rec['rows'][0]['name'] == 'name11'
        assert float(rec['rows'][0]['price']) == 12.1
        rec = self.db.update(_table='tmp_users', id=1, name='name11', price=12.1)  # 等值仍然更新成功
        # print(rec)
        assert rec == 1

    def test_delete(self):
        rec = self.db.delete(_table='tmp_users', id=1)
        print('delete:', rec)
        assert rec == 1
        rec = self.db.delete(_table='tmp_users', id=1)
        assert rec == 0


class TestPostgresql(CommTest):
    """postgresql数据接口的测试用例，主要测试CRUD操作"""

    def setup_class(self):  # 在开始测试之前进行的准备工作
        print('\ninit to test...', self.__class__.__name__)
        self.db = init(*private.conn_pg15, _debug=True)
        # self.db._begin()
        execute = self.db._execute
        # execute = self.db._cur.execute
        print('drop', execute("""drop table if exists tmp_users;"""))
        result = execute("""create table tmp_users(id serial primary key, 
            name varchar(100), age int, price decimal(10,2) ); """)
        print('create: ', result)

    def teardown_class(self):
        print('\nend to test')
        # self.db.close()
        self.db._execute('drop table if exists tmp_users')
        # self.db._cur.close()
        # self.db._con.close()
        del self.db


class TestSqlite3(CommTest):
    """sqlite3实例测试
    初始化类，通过DDL语句建表
    通过接口进行CRUD操作
    删除表，删除文件
    """

    def setup_class(self):  # 在开始测试之前进行的准备工作
        print('\ninit to sqlite3 test...')
        self.db = init('sqlite3', 'test.sqlite3', _debug=True)
        execute = self.db._execute
        execute("""drop table if exists tmp_users;""")
        execute("""create table tmp_users(id integer primary key autoincrement, 
            name varchar(100), age int, price decimal(10,2) ); """)

    def teardown_class(self):
        del self.db
