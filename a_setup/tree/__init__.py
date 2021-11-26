# -*- coding: utf-8 -*-
# $Header: D:\\RCS\\E\\dragonfly\\0_setup\\0_config\\__init__.py,v 1.0 2015-09-25 10:19:30+08 tgm Exp tgm $

import os
# import cfg
from .. import default as parent_default

name = 'Tree表设置'


class default(parent_default):
    """tree表的基本字段要求　：id 自增主键        parentid 上级id
    text 名称     state 状态字段，有下级时为closed，无下级为open
    path 路径，可选字段，为点字符连接的从根（０）记录到本记录的路径
    level 层级，可选字段，其中可视为path中连接符号点的数量
    注意，初始中并不存在id为０的记录，但parentid=0表示本记录是顶层记录
    """

    dirs = [os.path.dirname(__file__)] + parent_default.dirs
    table = 'org'

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
        self.dct['_real_table'] = self.dct['table'] = kw.pop('table', self.table)
        self.dct['table_kind'] = name
        self.dct['table_class'] = getattr(self.db, self.dct['table'])

    def delete(self, id):
        """为了做额外处理，拦截delete请求"""

        if self.db.select(self.table, id=id)['rows'][0]['state'] == 'closed':
            return {'isError': True, 'title': '错误', 'msg': "必须先删除下级节点"}
        parentid = self.db.select(self.table, id=id)['rows'][0]['parentid']
        # result = super(default, self).delete(id)
        result = self.db.delete(self.dct['table'], id)
        if not self.db.count(self.table, parentid=parentid):
            self.db.update(self.table, parentid, state='open')
        return {'success': True}

        return #    直接返回会停止删除？
        for r in self.db.select(self.table, parentid=id):
            default.delete(r['id'], 1)  # 递归删除下级时，depth为1
        self.db.delete(self.table, id)
        if not depth:   # 非递归删除下级时，才更新父记录的state字段
            parentid = self.db.select(self.table, id=id)['rows'][0]['id']
            if not self.db.count(self.table, parentid=parentid):
                self.db.update(self.table, parentid, state='open')
        table = self.dct['table']
        rec = self.db.select(table, id=id)['rows'][0]
        print('debug: delete:', table, id, rec)
        parentid = rec['parentid']
        # if rec['state'] == 'closed': # 如果有下级，不允许删除？
        #    return
        result = self.db.delete(self.dct['table'], id)
        if result:  
            # 要将本节点作为上级的全部子节点全部删除！
            recs = self.db.select(table, path=rec['path']+'.'+str(id)+'%')
            for rec in recs['rows']:
                self.db.delete(table, rec['id'])
            # 如果删除成功，则要考察父节点下面是否还有子节点，以更改状态
            par_rec = self.db.select(table, parentid=parentid)
            if not len(par_rec['rows']):
                self.db.update(table, parentid, state='open')
        return result

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
        kw['parentid'] = par = int(kw.pop('parentId'))  # tree里上级是用parentid表示的，不同于treegrid.
        kw['state'] = 'open'
        if self.db.count(self.table, parentid=par) >= self.MAX_CHILDREN:    # 下级数量限制
            return {'isError': True, 'title': 'error', 'msg': '下级数量超出限制'}
        kw['display'] = self.db.max(self.table, 'display', parentid=par) + 1
        if par > 0:     # 不是顶级目录，父记录的状态要置为可打开。
            self.db.update(self.table, par, state='closed')
        return super(default, self).insert(**kw)

    def select(self, *k, **kw):
        """自定义Get, 为了处理q参数"""

        """
        if kw.pop('_log','') == 'true':
            kw['table'] = self._dic['table'] + '_log'
        else:
            kw['table'] = self._dic.get('_real_table', self._dic['table'])
            """
        if 'q' in kw:
            kwq = kw.pop('q')
            if kwq.encode().isalpha():  # 是字母, 则对config_tables按表名查找
                kw['name'] = '%' + kwq + '%'
            else:
                kw['name_zh'] = '%' + kwq + '%'
        return super(default, self).select(*k, **kw)


__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])

# $Log: __init__.py,v $
# Revision 1.0  2015-09-25 10:19:30+08  tgm
# Initial revision
#
