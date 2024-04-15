# table_log: 自带日志记录的单表
# 适合于数据量不大，字段较少，没有频繁修改的数据表
# 特点：
# 1、不单列日志表。
# 2、可以复现任何时候的数据
# 3、修改总是在最新记录上进行
# 4、字段要求：有自增主键id，第二主键为真实主键，有一个表示修改时间的m_date。

import os

from .. import default as parent

name = "单表自带日志"


class default(parent):
    """
    设计思路：单表自带日志适用于数据量较小，日常变动也较小，字段数也比较少的情景。
    必须字段有：自增主键ID，数据主键字段（一般不可更改），状态时间，状态，其余字段。
    展示数据时，对每一个数据主键，只展示最后一条记录，或者不大于指定时间的最后一条记录。
    对字段的修改，会生成一条新的数据记录，状态时间为修改时的时间。
    对记录的删除，会生成一条新的数据记录，状态为失效，状态时间为删除时的时间。
    这样可以达到只使用一张表，没有复杂的关联关系的情况下，可以随时恢复展示任何时间点的数据状态。
    比较适用于员工资料，通讯录，固定资产资料等一些场景。
    """
    dirs = [os.path.dirname(__file__)] + parent.dirs
    table = 'table_log'

    def __init__(self, *k, **kw):
        super(default, self).__init__(k, kw)

    def select(self, m_time=None, **kw):
        """重写select，以便取得指定日期之前的，最大修改日期的副本。
        如不指定日期，则是指最新数据，可以进行修改"""

        pass

    def update(self, **kw):
        """重写更新函数，每次更新实际生成一笔新记录"""

        pass

    def delete(self, id):
        """重写delete，删除只是生成一笔状态为删除的新记录"""

        pass

    def insert(self, **kw):
        """重写insert，生成新记录前，要检查第二主键是否重复"""

        pass