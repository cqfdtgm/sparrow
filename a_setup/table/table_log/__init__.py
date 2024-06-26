# -*- coding: utf-8 -*-
# /a_setup/table/table_log/__init__.py


import datetime
import os

from .. import default as parent


class default(parent):
    """
    # table_log: 自带日志记录的单表
    # 适合于数据量不大，字段较少，没有频繁修改的数据表
    # 特点：
    # 1、不单列日志表。
    # 2、可以复现任何时候的数据
    # 3、修改总是在最新记录上进行
    # 4、字段要求：有自增主键id，第二主键为真实主键，有一个表示修改时间的mtime。可以有表示状态的字段state以标准注销。
    设计思路：单表自带日志适用于数据量较小，日常变动也较小，字段数也比较少的情景。
    必须字段有：自增主键ID，数据主键字段（一般不可更改），状态时间，状态，其余字段。
    展示数据时，对每一个数据主键，只展示最后一条记录，或者不大于指定时间的最后一条记录。
    对字段的修改，会生成一条新的数据记录，状态时间为修改时的时间。
    对记录的删除，会生成一条新的数据记录，状态为失效，状态时间为删除时的时间。
    这样可以达到只使用一张表，没有复杂的关联关系的情况下，可以随时恢复展示任何时间点的数据状态。
    比较适用于员工资料，通讯录，固定资产资料等一些场景。
    """
    dirs = [os.path.dirname(__file__)] + parent.dirs
    name = "单表自带日志"

    table = 'users_log'

    def __init__(self, *k, **kw):
        
        # self.table_kind = name
        super(default, self).__init__(*k, **kw)
        # self.dct['_real_table'] = self.dct['table'] = kw.pop('table', self.table)
        # self.dct['table_kind'] = name
        #　self.dct['table_class'] = getattr(self.db, self.dct['table'])

    def select(self, m_time=None, **kw):
        """重写select，以便取得指定日期之前的，最大修改日期的副本。
        如不指定日期，则是指最新数据，可以进行修改"""

        mtime = kw.pop('mtime', '') 
        if type(mtime) == type([]): # 提供了两个日期，则是在日志显示中为了按时段查看
            if mtime[0] and mtime[1]:   # 开始结束时间都选择
                kw['mtime'] = ['between', *mtime]
            elif mtime[0]:  # 只提供了开始时间
                kw['mtime'] = ['>=', mtime[0]]
            elif mtime[1]:  # 只提供了结束时间
                kw['mtime'] = ['<=', mtime[1]]
        elif mtime:   # 如果选择了穿越功能，则只显示该时间点以前的记录
            kw['mtime'] = ['<=', mtime]
        # partition = kw.pop('partition', '')
        # partition_by = kw.pop('partition_by', '')
        return super().select(**kw)

    def update(self, **kw):
        """重写更新函数，每次更新实际生成一笔新记录"""

        assert int(kw.pop('id', 0)) > 0  # 不能修改空记录
        kw.pop('id', 0)
        kw.pop('rn', '')    # rn是select时多出来的一个字段
        kw['mtime'] = datetime.datetime.now()
        kw['action'] = '修改'
        # 如何实现修改时不能修改did字段？
        # 在界面中展示只能修改业务字段，不能修改id, did, mtime, state, action等。
        rec = super().insert(**kw)
        return rec

    def delete(self, id):
        """重写delete，删除只是生成一笔状态为删除的新记录"""

        result = self.db.select(self.table, id=id)
        kw = result['rows'][0]
        kw.pop('id')
        kw['mtime'] = datetime.datetime.now()
        kw['state'] = '注销'
        kw['action'] = '注销'
        rec = super().insert(**kw)
        return dict(success=True, newid=rec['id'])

    def insert(self, **kw):
        """重写insert，生成新记录前，要检查第二主键是否重复"""

        kw['state'] = '有效'
        kw['action'] = '增加'
        kw['mtime'] = datetime.datetime.now()
        kw['did'] = self.db.max(table=self.table, column='did') + 1
        return super().insert(**kw)

    def log(self, *k, **kw):
        self.table_class = getattr(self.db, self.table)

__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])
