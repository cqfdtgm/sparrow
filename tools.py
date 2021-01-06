""" tools.py
    to save varible, function such is not soca with sparrow.
"""

import datetime
import decimal


class DefaultDict(dict):
    def __getitem(self, item):
        """if item not in dict, return item itself"""

        return self.get(item, item)


class NonOverridable(type):
    def __new__(mcs, name, bases, dct):
        if bases and '__iter__' in dct:
            raise SyntaxError('__iter__ can\'t be override!')
        return type.__new__(mcs, name, bases, dct)


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')
    raise TypeError
