# -*- coding: utf-8 -*-
# $Header: D:\\RCS\\E\\dragonfly\\0_setup\\0_config\\__init__.py,v 1.0 2015-09-25 10:19:30+08 tgm Exp tgm $

import os

# import cfg

from .. import default
from ... import tools

name = '树形数据网格'


class default(default):
    dirs = [os.path.dirname(__file__)] + default.dirs
    file = __file__
    _table = 'gbook'

    def __init__(self, *k, **kw):
        # kw.setdefault('_table','gbook')
        super(default, self).__init__(*k, **kw)
        #self._dic['_table_var_name'] = '_table_tree'
        #cherrypy.session.setdefault('_table_tree', 'org')
        #if '_table_tree' in kw:  # 通过右上角的"更改目标表"更改了表.
        #    cherrypy.session['_table_tree'] = kw.pop('_table_tree')
        #self._dic['_table'] = self._dic['table_form'] = cherrypy.session['_table_tree']
        #self._dic['_real_table'] = self._dic['_table'] = kw.pop('_table','gbook')
        #self._dic.setdefault('_table', kw['_table'])
        #self._dic.setdefault('_real_table', kw['_table'])
        self.dct['_real_table'] = self.dct['_table'] = kw.pop('_table', self._table)
        self.dct['table_kind'] = name
        self.dct['table_class'] = getattr(self.db, self.dct['_table'])

    def Get(self, *k, **kw):
        """自定义Get, 为了处理q参数
             test tset """

        # 这个是在什么情况下加的删除输入为空的条件? 会误解呃.
        """
        for k, v in list(kw.items()):
            if v=='':   # 删除输入为空的查询字段，往往是后面几级查询条件
                kw.pop(k)
                """
        if '_table' not in kw:
            if kw.pop('_log','') == 'true':
                kw['_table'] = self.dct['_table'] + '_log'
            else:
                kw['_table'] = self.dct.get('_real_table', self.dct['_table'])
        if 'q' in kw:
            kwq = kw.pop('q')
            if kwq.encode().isalpha():  # 是字母, 则对config_tables按表名查找
                kw['name'] = '%'+ kwq + '%'
            else:
                kw['name_zh'] = '%' + kwq + '%'
        # 如果kw里只有'id', 则是以此为父id展开下级记录，否则，是以指定条件查找相应记录
        if 'id' in kw:
            kw['parentid'] = kw.pop('id', 0)
        else:
            pass
        print('I am in 0_setup.treegrid', k, kw)
        if kw.get('parentid',0): #展下开级目录，原则上不限制数量，设计应该防止子记录过大
            kw.pop('page',0)
            #kw.pop('rows',0)
            kw['rows'] = 100
        result = result2 = super(default, self).Get(*k, **kw)
        """
        if not kw['parentid']: # 是根记录，展开一层
            #for r in result['rows']:
            #    r.pop('state', 0)
            kw2 = kw.copy()
            kw2.pop('page', 0)
            kw2['rows'] = -1
            kw2['parentid'] = [r['id'] for r in result2['rows']]
            result2 = super(default, self).Get(*k, **kw2)
            result['rows'] += result2['rows']
            print('parnet', kw2, len(result2['rows']))
        for r in result['rows']:
            if r['parentid']:
                r['_parentId'] = r['parentid']
        """
        if kw.get('parentid',0): # 上级不为0， 则是展开下级记录，只返回rows数据
            return result['rows']
        else:   
            return result

    def Save(self, *k, **kw):
        """为了保存path信息， 拦截Save请求并添加path字段。"""

        kw['name'] = self._sess.get('user','')
        kw['stime'] = tools._now()
        if kw.get('parentid',0):   # 是回复
            parent = self.Update(_table=self.dct['_table'], id=kw['parentid'], state='closed')
            # 同时要根据上级记录，更新level和path
            if 'level' in parent:
                kw['level'] = parent['level'] + 1
            if 'path' in parent:
                kw['path'] = '%s.%s' % (parent['path'],parent['id'])
        return super(default, self).Save(*k, **kw)

    def Update(self, *k, **kw):
        result = super(default, self).Update(*k, **kw)
        print('Update for ', kw, result)
        return result


__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])

# $Log: __init__.py,v $
# Revision 1.0  2015-09-25 10:19:30+08  tgm
# Initial revision
#
