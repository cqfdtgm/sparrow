﻿# -*- coding: utf-8 -*-
# \a_setup\tree\__init__.py

import os
from .. import default as parent


class default(parent):
    """tree表的基本字段要求: id 自增主键        parentid 上级id
    text 名称     state 状态字段，有下级时为closed，无下级为open
    path 路径，可选字段，为点字符连接的从根（０）记录到本记录的路径
    display 同级显示顺序，新增加的最大，同级拖动时会改变。
    level 层级，可选字段，其中可视为path中连接符号点的数量
    注意，初始中并不存在id为0的记录,但parentid=0表示本记录是顶层记录
    """

    dirs = [os.path.dirname(__file__)] + parent.dirs
    table = 'org'
    name = 'Tree表设置'

    MAX_CHILDREN = 10    # 下级数量限制，如果实现了翻页，下级数量不需要限制了。
    PAGESIZE = 4

    def __init__(self, *k, **kw):
        # kw.setdefault('table', 'org')
        super(default, self).__init__(*k, **kw)
        # self._dic['table_var_name'] = 'table_tree'
        # cherrypy.session.setdefault('table_tree', 'org')
        # if 'table_tree' in kw:  # 通过右上角的"更改目标表"更改了表.
        #    cherrypy.session['table_tree'] = kw.pop('table_tree')
        # self._dic['table'] = self._dic['table_form'] = cherrypy.session['table_tree']
        # self.table_kind = name
        # self.dct['_real_table'] = self.dct['table'] = kw.pop('table', self.table)
        # self.dct['table_kind'] = name
        # self.dct['table_class'] = getattr(self.db, self.dct['table'])

    def delete(self, id):
        """为了做额外处理，拦截delete请求"""

        if self.db.select(self.table, id=id)['rows'][0]['state'] == 'closed':
            return {'isError': True, 'title': '错误', 'msg': "必须先删除下级节点"}
        parent_id = self.db.select(self.table, id=id)['rows'][0]['parentid']
        # result = super(default, self).delete(id)
        self.db.delete(self.table, id)
        if not self.db.count(self.table, parentid=parent_id):
            self.db.update(self.table, parent_id, state='open')
        return {'success': True}

    def dnd(self, **kw):
        kw.setdefault('max_children', self.MAX_CHILDREN)
        return super(default, self).dnd(**kw)

    def tree(self, *k, **kw):
        """增加对于pagesize的参数，以例可以显示更多下级"""

        kw.setdefault('rows', self.PAGESIZE)
        return super(self.__class__, self).tree(*k, **kw)

    def insert(self, **kw):
        """为了保存path信息， 拦截Save请求并添加path字段。"""

        print('k kw @ 0_setup\\tree', kw)
        kw['parentid'] = par = int(kw.pop('parentid'))  # tree里上级是用parentid表示的，不同于tree_grid.
        kw['state'] = 'open'
        if self.db.count(self.table, parentid=par) >= self.MAX_CHILDREN:    # 下级数量限制
            return {'isError': True, 'title': 'error', 'msg': '下级数量超出限制'}
        kw['display'] = self.db.max(self.table, 'display', parentid=par) + 1
        kw['text'] = 'New Item'
        if par > 0:     # 不是顶级目录，父记录的状态要置为可打开。
            self.db.update(self.table, par, state='closed')
        return super(default, self).insert(**kw)


__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])
