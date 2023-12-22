# -*- coding: utf-8 -*-
# $Header: C:\\RCS\\D\\dragonfly\\0_setup\\table\\__init__.py,v 1.0 2017-04-27 10:35:24+08 $

import os
from .. import default

name = '行云单表'

# import dbapi2

class default(default):
    dirs = [os.path.dirname(__file__)] + default.dirs
    from .... import dbapi, private
    db_type, connect_str = private.conn_xy
    _table = 'latn_33_comp_main_config'

    def __init__(self, *k, **kw):
        kw.setdefault('_table', self.__class__._table)
        super(default, self).__init__(*k, **kw)
        # self._dic['_table_var_name'] = table = '_table_a'
        # cherrypy.session.setdefault(table, 'cfg_tables')
        # if _table in kw:  # 通过右上角的"更改目标表"更改了表.
        #    cherrypy.session['_table'] = kw.pop(table)
        # self._dic['_table'] = self._dic['table_form'] = cherrypy.session['_table']
        # 不在session中保存当前表名， 而在客户端页面保存，以便session失效时，也能正确展示页面。需要在页面中各种URL地方添加_table关键字后缀。这样同一用户打开多个页面时也不会互相冲突。
        self._dic['_real_table'] = self._dic['_table'] = kw.pop('_table', 'cfg_tables')
        self._dic['table_kind'] = name
        self._dic['table_class'] = getattr(self.db, self._dic['_table'])

__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])

# $Log: __init__.py,v $
# Revision 1.0  2017-04-27 10:35:24+08  u?????
# Initial revision
#
# Revision 1.0  2015-09-25 10:19:30+08  tgm
# Initial revision
#
