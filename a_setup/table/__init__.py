# -*- coding: utf-8 -*-
# $Header: C:\\RCS\\D\\dragonfly\\0_setup\\table\\__init__.py,v 1.0 2017-04-27 10:35:24+08 $

import os
# import cfg
from .. import default as parent
# , tools, sparrow, private, dbapi2

name = 'A单表设置'


class default(parent):
    dirs = [os.path.dirname(__file__)] + parent.dirs
    table = 'cfg_tables'
    table_kind = name

    def __init__(self, *k, **kw):
        super(default, self).__init__(*k, **kw)
        # self._dic['_table_var_name'] = table = '_table_a'
        # cherrypy.session.setdefault(table, 'cfg_tables')
        # if _table in kw:  # 通过右上角的"更改目标表"更改了表.
        #    cherrypy.session['_table'] = kw.pop(table)
        # self._dic['_table'] = self._dic['table_form'] = cherrypy.session['_table']
        # 不在session中保存当前表名， 而在客户端页面保存，以便session失效时，也能正确展示页面。需要在页面中各种URL地方添加_table关键字后缀。
        self.dct['_real_table'] = self.dct['table'] = kw.pop('table', self.table)
        self.dct['table_kind'] = name
        self.dct['table_class'] = getattr(self.db, self.dct['table'])

    def select(self, *k, **kw):
        """自定义Get, 为了增加对q参数的处理"""

        if 'q' in kw:
            kwq = kw.pop('q')
            if kwq.encode().isalpha():   # 是字母, 则对config_tables按表名称模糊查询
                kw['name'] = '%'+kwq+'%'
            else:
                kw['name_zh'] = '%' + kwq+'%'   # 否则按中文名
        print('k kw @ 0_setup.table.Get', k, kw)
        return super(default, self).select(*k, **kw)


__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])
