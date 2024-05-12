# -*- coding: utf-8 -*-
# $Header: C:\\RCS\\D\\dragonfly\\0_setup\\table_detail\\__init__.py,v 1.0 2017-04-27 10:35:30+08 $

import os

# import cfg

from .. import default
class default(default):
    dirs = [os.path.dirname(__file__)] + default.dirs
    name = '数据网格视图'

    def __init__(self, *k, **kw):
        kw.setdefault('_table', 'gbook')
        super(default, self).__init__(*k, **kw)
        self.dct['_real_table'] = self.dct['_table'] = kw.pop('_table', 'gbook')
        self.dct['table_kind'] = name
        #print('k，kw @ 0_setup.table_detail', k, kw, self._dic)

    def Get(self, *k, **kw):
        """自定义Get, 为了增加对q参数的处理"""

        """
        if 'q' in kw:
            kwq = kw.pop('q')
            if kwq.encode().isalpha():   # 是字母, 则对config_tables按表名称模糊查询
                kw['name'] = '%'+kwq+'%'
            else:
                kw['name_zh'] = '%' + kwq+'%'   # 否则按中文名
        """
        desc =  getattr(self.db_class, self.dct['_table'])._desc
        cols = [i[0] for i in desc]
        #print('COLS', desc, cols)
        if 'parentid' in cols:
            kw.setdefault('parentid', 0)
        result = result2 = super(default, self).Get(*k, **kw)
        #print('self._dic, db', self._dic, kw)
        return result

    def Save(self, *k, **kw):
        """增加用户名和时间字段的值"""

        kw['name'] = self._sess.get('user','')
        kw['stime'] = tools._now()
        if kw.get('parentid',0):   # 是回复，则需要将上级贴的state修改为closed
            tb = getattr(self.dct['_db'], self.dct['_table'])
            rec= tb(kw['parentid'])
            rec.state = 'closed'
            rec.childrens += 1
            #self.Update(_table=self._dic['_table'], id=kw['_parentid'], state='closed')
        return super(default, self).Save(*k, **kw)

__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])

# $Log: __init__.py,v $
# Revision 1.0  2017-04-27 10:35:30+08  u????ү
# Initial revision
#
# Revision 1.0  2015-09-25 10:19:30+08  tgm
# Initial revision
#
