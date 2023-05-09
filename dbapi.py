# dbapi.py
# access to the database
# most simple database access of crud
#

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
# import pytest
import sqlite3
# import sys
# import traceback

# from . import private


def init(db_type, connect_str, _debug=True, _autocommit=True):
    """返回由db_type指定类型，connect_str指定具体连接的数据库对象
    目前本文件中定义了以下db_type及连接字符串格式:
    sqlite3, test.sqlite3
    """

    db_type = db_type.capitalize()  # 首字母大写以符合类名规范
    return globals()['Database' + db_type](connect_str, _debug, _autocommit)


class Database(abc.ABC):
    """A class to access database, define CRUD
    只提供简单的CRUD接口，和commit, rollback, begin接口，默认自动提交 ，
    事务由调用者控制。
    SQL保留字不能用作表名或者字段名：select, insert, delete, update, commit,
    begin, rollback, count, 所以这些方法可以不加下划线。
    如何防范ＳＱＬ注入？
    """

    _param_style = ""
    _limit = ""
    # _limit_0 = ""
    _connect = None

    def __init__(self, _connect_str, _debug, _autocommit):
        print('init in Database:', _connect_str, _debug, _autocommit)
        self._connect_str = _connect_str
        self._debug = _debug
        self._autocommit = _autocommit

    def __del__(self):
        self.commit()
        if 'cursor' in self.__dict__:
            self.cursor.close()
            self.connect.close()

    def __getattr__(self, table):
        """未访问过的表，会将其字段结构取来，作为类的属性，该表用select返回的类cur对象表示"""
        if not table.startswith('_'):
            table_class = self.select(table, rows=0)
            setattr(self.__class__, table, table_class)
            return table_class

    @property
    def connect(self):
        """只在访问该属性才才建立连接，并设为属性，避免二次连接i"""

        # print('connect @ abc..', self.connect)
        if '_con' not in self.__dict__:
            # print('con:', self._connect, self._connect_str)
            self.__dict__['_con'] = self.__class__._connect(self._connect_str)
            # self._con.autocommit == self._autocommit
        return self.__dict__['_con']

    @property
    def cursor(self):
        """只在需要时才建立游标，并设为属性，避免二次建立 """

        if 'cursor' not in self.__dict__:
            self.__dict__['cursor'] = self.connect.cursor()
        return self.__dict__['cursor']

    def commit(self):
        if '_con' in self.__dict__:
            self.connect.commit()

    def select(self, table, column="*", rows=10, page=1, order="", **kw):
        """select data from database
        这些参数尽量用下划线，是为了防止与表名相冲突
        order: 每个数据库的实现不一样,格式为“order by col1 [asc|desc], col2[asc|desc]”
        分页控制相关: 每个数据库的实现不一样，由rows, page运算得start，结合数据库的limit字句定义而来。
        kw: key is column of table, value is column's value
        select的返回结果除了给default中的select使用以外，还会设置字段列表等属性，并置为数据库的表属性。
        sql保留字，python保留字，以及rows,page(easyui的保留字),不能用于数据库表名和字段名。
        """

        start = (page-1) * rows
        limit = self._limit % locals()
        if order:
            order = "order by " + order
        sql = "select %(column)s from %(table)s %(wheres)s %(order)s" \
              "%(limit)s"
        # print('locat @ dbapi.select:', locals())
        wheres, values = self.where(**kw)
        sql = sql % locals()
        # print('kw:', kw, wheres, values)
        cur = self.execute(sql, values)
        result = dict()
        result['data'] = cur.fetchall()
        result['desc'] = cur.description
        result['description'] = cur.description
        result['columns'] = [i[0].lower() for i in cur.description]
        result['rows'] = [dict(zip(result['columns'], i)) for i in result['data']]
        result['rowcount'] = len(result['data'])
        return result

    def count(self, table, page=1, rows=10, order='', **kw):
        """统计kw条件的记录数量，用于select返回total值，客户端展示分页"""

        wheres, values = self.where(**kw)
        sql = "select count(*) as cnt from %(table)s %(wheres)s"
        sql = sql % locals()
        cur = self.execute(sql, values)
        result = cur.fetchall()[0][0]
        # print('count:', result)
        return result

    def max(self, table, column, **kw):
        """统计kw条件的column字段最大值"""

        wheres, values = self.where(**kw)
        sql = """select max(%(column)s) from %(table)s %(wheres)s"""
        sql = sql % locals()
        result = self.execute(sql, values).fetchall()[0][0] or 0
        # print('max:', result)
        return result

    def insert(self, table, **kw):
        """返回新插入的记录的id"""

        sql = "insert into %(table)s (%(columns)s) values (%(values)s)"
        columns = ",".join(kw.keys())
        values = ",".join([self._param_style] * len(kw))
        sql = sql % locals()
        cur = self.execute(sql, list(kw.values()))
        return cur.fetchall()[0][0]

    def delete(self, table, id):
        """返回受影响的行数"""

        sql = "delete from %(table)s where id=%(id)s"
        sql = sql % locals()
        result = self.execute(sql, [])
        return result.rowcount

    def update(self, table, id, **kw):
        """返回更新成功的受影响的行数"""

        sql = "update %(table)s set %(changes)s where id=%(id)s"
        changes = ",".join(" %s=%s " % (column, self._param_style)
                           for column in kw)
        sql = sql % locals()
        result = self.execute(sql, list(kw.values()))
        return result.rowcount

    def where(self, **kw):
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
            elif isinstance(value, (list, tuple)):
                if value[0] in ('>', '<', '>=', '<='):
                    wheres.append("""%s %s %s""" % (column, value[0], self._param_style))
                    values.append(value[1])
                else:   # in , not in, is null, is not null...
                    raise
        wheres = " where " + " and ".join(wheres)
        """if wheres:
            wheres = " where " + ' and '.join(wheres)
        else:
            wheres = ''
            """
        return wheres, values

    def execute(self, sql, values=()):
        """使用本类中初始化的con, cur来执行SQL语句，并返回结果。
        本方法并不进行事务方面的处理，事务由本方法的调用者处理
        要在本处套一层，是为了方便行云的处理。行云需要通过队列在其他进程中执行，而且只能返回一个类cur的东西。
        """

        if self._debug:
            print(self._debug, 'SQL @ execute: ', sql, values, self.__class__.__name__)
        assert ';' not in sql   # 防范SQL注入
        cur = self.cursor
        cur.execute(sql, values)
        return cur


class DatabasePostgresql(Database):
    """继承自Database, 具体指定了数据库类型为postgresql"""

    _param_style = '%s'
    _limit = " limit %(rows)s offset %(start)s "     # pgsql分页子句 limit rows offset pages , 其中offset子句可省略，
    # 省略时其默认为offset 0，表示从第1条记录开始。rows参数表示限制输出行数，即每页记录数。多页时，page应是（页数－1）乘以每页行数
    # _limit_0 = _limit % {'rows': 0, 'start': 0, 'page': 0}
    _connect = psycopg2.connect

    def autocommit(self):
        self.connect.autocommit = True

    def insert1(self, table, **kw):
        """覆写再调用，插入后需要执行lastval()以取得上次插入的记录id"""
        super(DatabasePostgresql, self).insert(table, **kw)
        if 'id' in kw:
            return kw['id']
        else:
            lastrowid = self.execute("select lastval() as id").fetchall()[0][0]
            return lastrowid

    def insert(self, table, **kw):
        """通过添加reuturnging id来现场返回id"""

        sql = "insert into %(table)s (%(columns)s) values (%(values)s) returning id"
        columns = ",".join(kw.keys())
        values = ",".join([self._param_style] * len(kw))
        sql = sql % locals()
        cur = self.execute(sql, list(kw.values()))
        return cur.fetchall()[0][0]


class DatabaseSqlite3(Database):

    _param_style = '?'
    _limit = " limit %(start)s, %(rows)s "
    # _limit_0 = _limit % {'rows': 0, 'start': 0, 'page': 0}
    _connect = sqlite3.connect

    def insert(self, table, **kw):
        """返回新插入的记录的id"""

        sql = "insert into %(table)s (%(columns)s) values (%(values)s)"
        columns = ",".join(kw.keys())
        values = ",".join([self._param_style] * len(kw))
        sql = sql % locals()
        cur = self.execute(sql, list(kw.values()))
        return cur.lastrowid


# 本文件与框架无关，所以可能单独进行单元测试
# 测试方式： pytest dbapi.py
class CommTest(abc.ABC):
    """公共测试基类，不实际测试，所以不能以Test开头"""

    db = None

    @abc.abstractmethod
    def setup_class(self):
        pass

    def teardown_class(self):
        self.db.execute('drop table if exists tmp_users')
        self.db.cursor.close()
        self.db.connect.close()

    def test_insert(self):
        new_id = self.db.insert('tmp_users', name='name1', age=1, price=1.1)
        print('new_id, ', self.__class__.__name__, new_id)
        assert new_id == 1
        for i in range(2, 21):
            new_id = self.db.insert('tmp_users', name='name%s' % i, age=i, price=i+0.1)
            assert new_id == i
        # 指定id的插入，pg不能返回正确的lastrowid, sqlite是可以的
        new_id = self.db.insert('tmp_users', id=27, name='name27', age=2, price=2.1)
        assert new_id == 27
        new_id = self.db.insert('tmp_users', id=25, name='name25', age=3, price=3.1)
        assert new_id == 25

    def test_select_one(self):
        rec = self.db.select('tmp_users', id=1)
        print('rec @ test_select_one:', self.__class__.__name__, rec)
        assert rec['rowcount'] == 1
        assert rec['columns'] == ['id', 'name', 'age', 'price']
        assert rec['rows'][0]['id'] == 1
        assert rec['rows'][0]['name'] == 'name1'
        # print(dir(row['price']))
        # print('%s' % row['price'], float(row['price']))
        assert float(rec['rows'][0]['price']) == 1.1

    def test_select_multi(self):
        rec = self.db.select('tmp_users', order='id desc')
        assert len(rec['rows']) == 10
        rows = rec['rows']
        assert rows[0]['id'] == 27
        assert rows[1]['id'] == 25
        assert rows[2]['id'] == 20
        rec = self.db.select('tmp_users', name='%e1%', order='id desc')
        assert len(rec['rows']) == 10
        assert rec['rows'][0]['id'] == 19

    def test_select_multi_page(self):
        rec = self.db.select('tmp_users', order='id ', page=2, rows=10)
        assert len(rec['rows']) == 10
        assert rec['rows'][0]['id'] == 11
        assert rec['rows'][1]['id'] == 12
        assert rec['rows'][-1]['id'] == 20

    def test_count(self):
        cnt = self.db.count('tmp_users')
        assert cnt == 22
        cnt = self.db.count('tmp_users', name='%e1%')
        assert cnt == 11
        cnt = self.db.count('tmp_users', name=['>', 'name7'])
        assert cnt == 2

    def test_update(self):
        rec = self.db.update('tmp_users', id=1, name='name11', price=12.1)
        print('update of sqlite:', rec)
        assert rec == 1
        rec = self.db.select('tmp_users', id=1, column="id,name,price")
        assert rec['rows'][0]['name'] == 'name11'
        assert float(rec['rows'][0]['price']) == 12.1
        rec = self.db.update('tmp_users', id=1, name='name11', price=12.1)  # 等值仍然更新成功
        # print(rec)
        assert rec == 1

    def test_max(self):
        res = self.db.max('tmp_users', 'id')
        assert res == 27
        res = self.db.max('tmp_users', 'id', name='name1%')
        assert res == 19

    def test_delete(self):
        rec = self.db.delete('tmp_users', id=1)
        print('delete:', rec)
        assert rec == 1
        rec = self.db.delete('tmp_users', id=1)
        assert rec == 0


class TestPostgresql(CommTest):
    """postgresql数据接口的测试用例，主要测试CRUD操作"""

    def setup_class(self):  # 在开始测试之前进行的准备工作
        print('\ninit to test...', self.__class__.__name__)
        # from . import private
        import private
        self.db = init(*private.conn_pg15, _debug=False)
        # self.db._begin()
        execute = self.db.execute
        # execute = self.db.cursor.execute
        print('drop', execute("""drop table if exists tmp_users"""))
        result = execute("""create table if not exists tmp_users(id serial primary key, name varchar(100), age int, price decimal(10,2) ) """)
        print('create: ', result)


class TestSqlite3(CommTest):
    """sqlite3实例测试
    初始化类，通过DDL语句建表
    通过接口进行CRUD操作
    删除表，删除文件
    """

    def setup_class(self):  # 在开始测试之前进行的准备工作
        print('\ninit to sqlite3 test...')
        self.db = init('sqlite3', 'test.sqlite3', _debug=True)
        execute = self.db.execute
        execute("""drop table if exists tmp_users""")
        execute("""create table if not exists tmp_users(id integer primary key autoincrement, name varchar(100), age int, price decimal(10,2) ) """)
