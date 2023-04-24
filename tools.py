""" tools.py
    to save varibles, function such is not soca with sparrow.
"""

import datetime
import decimal


class DefaultDict(dict):
    def __getitem__(self, item):
        """if item not in dict, return item itself"""

        return self.get(item, item)


def decimal_default(obj):
    """为转换json数据写的默认值函数"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')
    raise TypeError


def test_defaultdict():
    assert DefaultDict()['a'] == 'a'
    assert DefaultDict()[3] == 3
    assert DefaultDict()[3.0] == 3
    assert DefaultDict()[''] == ''
    assert DefaultDict()[None] is None
