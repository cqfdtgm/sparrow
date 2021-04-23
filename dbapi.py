# dbapi.py
# access to the database

"""
Only special CRUD to a database, map to SQL:
C-create -> insert
R-recieve -> select
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


def init(db_type, connect_str, _debug=False):
    """返回由db_type指定类型，connect_str指定具体连接的数据库对象
    目前本文件中定义了以下db_type及连接字符串格式:
    sqlite3, test.sqlite3
    """

    return globals()['Database_' + db_type](connect_str, _debug)


class Database(abc.ABC):
    """A class to access database, define CRUD"""

    _param_style = ""
    _limit = ""
    _limit_0 = ""

    def __init__(self, _connect_str, _debug=False):
        self._connect_str = _connect_str
        self._debug = _debug

    def __del__(self):
        if 'conn' in self.__dict__ and self._con is not None:
            self._cur.close()
            self._conn.close()

    def __getattr__(self, _table):
        if not _table.startswith('_'):
            table = self._select(_table, _limit=self._limit_0)
            setattr(self.__class__, _table, table)
            return table

    def _select(self, _table="", _columns="*", _order="", _limit="", **kw):
        """select data from database
        kw: key is column of table, value is column's value
        """

        self._kw = kw
        sql = "select %(_columns)s from %(_table)s %(wheres)s %(_order)s" \
              "%(_limit)s"
        wheres, values = self._where_process(**kw)
        _order = "order by " + _order if _order else _order
        sql = sql % locals()
        print('kw:', kw, wheres, values)
        return self._query(sql, values)

    def _count(self, _table="", **kw):

        wheres, values = self._where_process(**kw)
        sql = "select count(*) as cnt from %(_table)s %(wheres)"
        sql = sql % locals()
        return self._query(sql, values)['rows'][0]['cnt']

    def _insert(self, _table="", **kw):

        self._kw = kw
        sql = "insert into %(_table)s (%(columns)s) values (%(values)s)"
        columns = ",".join(kw.keys())
        values = ",".join([self._param_style] * len(kw))
        sql = sql % locals()
        return self._query(sql, list(kw.values()))['lastrowid']

    def _delete(self, _table="", id=None):

        sql = "delete from %(_table)s where id=%(id)s"
        sql = sql % locals()
        result = self._query(sql, [])
        return result['rowcount']

    def _update(self, _table="", id=None, **kw):

        sql = "update %(_table)s set %(changes)s where id=%(id)s"
        changes = ",".join(" %s=%s " % (column, self._param_style)
                           for column in kw)
        sql = sql % locals()
        result = self._query(sql, list(kw.values()))
        # 如果更新成功，应返回该条记录的结果字典
        if result['rowcount'] == 1:
            return self._select(_table=_table, id=id)['rows'][0]
        # return result['rowcount']

    def _where_process(self, **kw):
        wheres, values = ['1=1'], []
        for column, value in kw.items():
            if isinstance(value, str):
                if '%' in value:
                    wheres.append("%s like %s" % (column, self._param_style))
                    values.append(value)
                else:
                    wheres.append("%s = %s" % (column, self.param_style))
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

    @abc.abstractmethod
    def _query(self, sql, values):
        """must be override, to return such as this"""

        assert self._connect_str
        assert sql
        assert values
        return {'data': '',
                'rows': [{'id': 0, 'column1': 'a'}, {'id': 1, 'column1': 'b'}],
                'desc': [], 'columns': ['a', 'b'], 'lastrowid': 0,
                'rowcount': 0, 'rownumber': 0, 'success': True}


class Database_postgresql(Database):
    """继承自Database, 具体指定了数据库类型为postgresql"""

    _param_style = '%s'
    _limit = " limit %(pagesize)s offset %(start)s "
    _limit_0 = _limit % {'pagesize': 0, 'start': 0}

    # def __init__(self, _connect_str="", _debug=False):
    #    super(self.__class__, self).__init__(_connect_str, _debug)

    def __getattr__(self, attr):
        """当需要访问self._con时，才实际建立连接"""

        if attr in ('_con', '_cur'):
            self._con = psycopg2.connect(self._connect_str)
            self._cur = self._con.cursor()
            return self._con if attr == '_con' else self._cur
        else:
            print('attr @ postgresql: ', attr)
            return super(self.__class__, self).__getattr__(attr)

    def _select(self, *k, **kw):
        """要重写，以便转换适用于easyui的翻页参数名称"""

        kw_s = dict()
        kw_s['pagesize'] = kw.pop('_pagesize', 10)
        kw_s['page'] = kw.pop('page', 1)
        kw_s['start'] = (kw_s['page'] - 1) * kw_s['pagesize']
        kw['_limit'] = self._limit % kw_s
        return super(self.__class__, self)._select(*k, **kw)

    def _commit(self):
        self._con.commit()

    def _rollback(self):
        self._con.rollback()

    def _begin(self):
        self._con.commit()
        self._con.autocommit = True

    def _query(self, sql, values=()):
        """使用本类中初始化的con, cur来执行SQL语句，并返回结果。
        本方法并不进行事务方面的处理，事务由本方法的调用者处理
        """

        result = dict()
        if self._debug:
            print('SQL @ _query: ', sql, values)
        self._cur.execute(sql, values)
        result['rowcount'] = self._cur.rowcount
        result['rownumber'] = self._cur.rownumber
        if sql.startswith('select'):
            result['data'] = self._cur.fetchall()
            result['desc'] = self._cur.description
            result['description'] = self._cur.description
            result['columns'] = [i[0].lower() for i in self._cur.description]
            result['rows'] = [dict(zip(result['columns'], i)) for i in result['data']]
        elif sql.startswith('insert'):  # insert是否需要显示获取lastrowid?
            # print('lastrowid', dir(self._cur), self._cur.lastrowid)
            if 'id' in self._kw:
                result['lastrowid'] = self._kw['id']
            else:
                self._cur.execute('select lastval()')
                result['lastrowid'] = self._cur.fetchall()[0][0]
        return result


class Database_sqlite3(Database):

    _param_style = '?'
    _limit = " limit %(pagesize)s offset %(start)s "
    _limit_0 = _limit % {'pagesize': 0, 'start': 0}

    def __getattr__(self, attr):
        if attr in ('_con', '_cur'):
            self._con = sqlite3.connect(self._connect_str)
            self._cur = self._con.cursor()
            return self._con if attr == '_con' else self._cur
        else:
            print('attr @ postgresql: ', attr)
            return super(self.__class__, self).__getattr__(attr)

    def _query(self, sql, values=()):
        """使用本类中初始化的con, cur来执行SQL语句，并返回结果。
        本方法并不进行事务方面的处理，事务由本方法的调用者处理
        """

        result = dict()
        if self._debug:
            print('SQL @ _query: ', sql, values)
        self._cur.execute(sql, values)
        result['rowcount'] = self._cur.rowcount
        result['lastrowid'] = self._cur.lastrowid
        if sql.startswith('select'):
            # sqlite3在select时rowcount仍然为-1，只有在insert, update, delete时，为真正变更的记录数
            result['data'] = self._cur.fetchall()
            result['rowcount'] = len(result['data'])
            result['desc'] = self._cur.description
            result['description'] = self._cur.description
            result['columns'] = [i[0].lower() for i in self._cur.description]
            result['rows'] = [dict(zip(result['columns'], i)) for i in result['data']]
        return result


# 本文件与框架无关，所以可能单独进行单元测试


def test_not_exists_dbtype():
    """空的或错误的数据库类型会引发keyError错误，因为本文件全局变量中没有Database_xx这个数据库类型"""

    with pytest.raises(KeyError):
        init('', '')


def test_not_instance():
    """测试：抽象基类不能直接实例化"""

    with pytest.raises(TypeError):
        Database('')


class Comm_test(abc.ABC):
    """公共测试基类，不实际测试，所以不能以Test开头"""

    @abc.abstractmethod
    def setup_class(self):
        pass

    @abc.abstractmethod
    def teardown_class(self):
        pass

    def test_insert(self):
        new_id = self.db._insert(_table='tmp_users', name='name1', age=1, price=1.1)
        assert new_id == 1
        new_id = self.db._insert(id=7, _table='tmp_users', name='name2', age=2, price=2.1)
        assert new_id == 7
        new_id = self.db._insert(id=5, _table='tmp_users', name='name3', age=3, price=3.1)
        assert new_id == 5

    def test_select_one(self):
        rec = self.db._select(_table='tmp_users', id=1)
        print(rec)
        assert rec['rowcount'] == 1
        assert rec['columns'] == ['id', 'name', 'age', 'price']
        row = rec['rows'][0]
        assert row['id'] == 1
        assert row['name'] == 'name1'
        assert row['age'] == 1
        # print(dir(row['price']))
        # print('%s' % row['price'], float(row['price']))
        assert float(row['price']) == 1.1

    def test_select_multi(self):
        rec = self.db._select(_table='tmp_users', _order='id desc')
        # print(rec)
        assert rec['rowcount'] == 3
        assert rec['rows'][0]['id'] == 7
        assert rec['rows'][1]['id'] == 5
        assert rec['rows'][2]['id'] == 1
        rec = self.db._select(_table='tmp_users', name='%e2%', _order='id desc')
        assert rec['rowcount'] == 1
        assert rec['rows'][0]['id'] == 7

    def test_update(self):
        rec = self.db._update(_table='tmp_users', id=1, name='name11', price='12.1')
        print('update of sqlite:', rec)
        assert rec['name'] == 'name11'
        assert float(rec['price']) == 12.1
        rec = self.db._update(_table='tmp_users', id=1, name='name11', price='12.1')  # 等值仍然更新成功
        # print(rec)
        assert rec['name'] == 'name11'
        assert float(rec['price']) == 12.1

    def test_delete(self):
        rec = self.db._delete(_table='tmp_users', id=1)
        print('delete:', rec)
        assert rec == 1
        rec = self.db._delete(_table='tmp_users', id=1)
        assert rec == 0
        pass


class Test_postgresql(Comm_test):
    """postgresql数据接口的测试用例，主要测试CRUD操作"""

    def setup_class(self):  # 在开始测试之前进行的准备工作
        print('\ninit to test...')
        self.db = init(*private.conn_pg15, _debug=True)
        query = self.db._query
        query("""drop table if exists tmp_users;""")
        query("""create table tmp_users(id serial primary key, 
            name varchar(100), age int, price decimal(10,2) ); """)

    def teardown_class(self):
        print('\nend to test')
        # self.db.close()
        self.db._query('drop table if exists tmp_users')
        self.db._cur.close()
        self.db._con.close()
        del self.db


class Test_sqlite3(Comm_test):
    """sqlite3实例测试
    初始化类，通过DDL语句建表
    通过接口进行CRUD操作
    删除表，删除文件
    """

    def setup_class(self):  # 在开始测试之前进行的准备工作
        print('\ninit to sqlite3 test...')
        self.db = init('sqlite3', 'test.sqlite3', _debug=True)
        query = self.db._query
        query("""drop table if exists tmp_users;""")
        query("""create table tmp_users(id integer primary key autoincrement, 
            name varchar(100), age int, price decimal(10,2) ); """)

    def teardown_class(self):
        self.db._cur.close()
        self.db._con.close()
        del self.db


if __name__ == '__main__':
    # 非框架相关的文件，直接在文件后半截进行测试编写，以本种方式指定文件名运行测试。
    # 不能单独对此文件进行测试，而是以文件所在文件夹为根，进行测试。且测试无法发现普通文件中的test_方法；
    # 只能发现test_*.py中的方法或者类
    pytest.main()
