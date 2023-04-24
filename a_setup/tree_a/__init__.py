# -*- coding: utf-8 -*-
# $Header: D:\\RCS\\E\\dragonfly\\0_setup\\0_config\\__init__.py,v 1.0 2015-09-25 10:19:30+08 tgm Exp tgm $

import os
# import cfg
from .. import default as pardefault

name = 'T-A关系设置'


class default(pardefault):
    dirs = [os.path.dirname(__file__)] + pardefault.dirs

    def __init__(self, *k, **kw):
        kw.setdefault('table', 'org_users')
        super(self.__class__, self).__init__(*k, **kw)
        """self._dic['table_var_name'] = '_tree_a'
        cherrypy.session.setdefault('_tree_a', 'org_users')
        cherrypy.session.setdefault('_tree_a_add1', '不可重复')
        if '_tree_a' in kw:  # 通过右上角的"更改目标表"更改了表.
            cherrypy.session['_tree_a'] = kw.pop('_tree_a')
            # 要取保留字段add1的值, 为"不可重复",或"可重复".
            tbl = getattr(cfg.db1, 'cfg_tables')
            rec = tbl(name=cherrypy.session['_tree_a'])
            cherrypy.session['_tree_a_add1'] = rec.add1
        self._dic['table'] = cherrypy.session['_tree_a'].split('_')[0]
        # AZ关系表中，真实表名总是字母序在前面。
        self._dic['_tree_a'] = '_'.join(sorted(cherrypy.session['_tree_a'].split('_')))
        self._dic['table_form'] = cherrypy.session['_tree_a']
        self._dic['table_z'] = cherrypy.session['_tree_a'].split('_')[1]
        """
        self.dct['table'] = table_az = kw.pop('table', 'org_users')
        # self._dic.setdefault('_az_add1','不可重复') # org_users 是不可重复关系
        # if 1:   #'chg' in kw:   每次都刷新add1字段？
        #    rec = cfg.db1.cfg_tables(name=self._dic['table'])
        #    self._dic['_ta_add1'] = rec.add1
        self.dct['table_a'], self.dct['table_z'] = table_az.split('_')
        self.dct['table_az'] = '_'.join(sorted(table_az.split('_')))
        # self.dct['_ta_add1'] = cfg.dic_add1[self.dct['table_az']]
        self.table_az = self.kw.pop('table_az', 'table_a')
        self.dct['real_table'] = self.dct[self.table_az]
        self.dct['table_kind'] = name

    def tree(self, *k, **kw):

        kw['table'] = self.dct['real_table']
        return super(default, self).tree(*k, **kw)

    def delete(self, *k, **kw):
        """转换id与id[]"""

        ids = kw.pop('id', [])
        if type(ids) != type([]):
            ids = [ids]
        for r in ids:
            super(self.__class__, self).delete(table=self.dct['real_table'], id=int(r))
        return dict(success="true")

    def select(self, *k, **kw):
        """自定义Get, 为了增加对q参数的处理"""

        if kw.pop('_log','') == 'true':
            kw['table'] = self.dct['table_az'] + '_log'
        else:
            kw['table'] = self.dct.get('real_table', self.dct['table'])
        #if self._dic['table'] in kw:   # 要记住上次点了哪一行
        #    cherrypy.session['ida'] = kw[self._dic['table']]
        #elif kw['table']==self._dic['_tree_a']: # 是取A端表
        #    kw[self._dic['table']] = cherrypy.session['ida']
        # 如果是取Z表数据, 则去除a端表限制, 另有not in来表示.
        if 'q' in kw: # 对q参数的处理
            kwq = kw.pop('q')
            if kwq.encode().isalpha():   # 是字母, 则对config_tables按表名称模糊查询
                kw['name'] = '%'+kwq+'%'
            else:
                kw['name_zh'] = '%' + kwq+'%'   # 否则按中文名
        if kw.pop('notin','false')=='true': # 对Z端表的排除查询需要用到notin参数, 这样可以避免使用两表join.
            kwa = {}
            ida = kw.pop(self.dct['table_a'], '')
            if self.dct['_ta_add1'] != '不可重复':
                # 可重复的情况下, 只将本节点已经选取的Z端记录排除；不可重复的情况下, 不限定条件, 则是将所有已经在tree_a表中出现的z端排除.
                print('可重复')
                kwa[self.dct['table_a']] = ida
            # has = getattr(cfg.db1, self.dct['_table_az'])(rows=100, _values_1=False, **kwa)
            # has = getattr(has, self.dct['_table_z'])
            #has = list(has)
            if len(has):
                kw['id'] = ['not in', has]
        # 处理include参数, 表示是否连带展示下级数据.
        if kw.pop('include', 'false')=='true': # 要展下示级数据
            # tb = getattr(cfg.db1, self.dct['table_a'])
            rec = tb(kw[self.dct['table_a']])
            #rec = tb(cherrypy.session['ida'])
            path = rec.path
            rec2 = tb(path = '%s.%s%s' % (path, kw[self.dct['table_a']], '%'))
            print('下级数据', rec2.id)
            if len(rec2):
                kw[self.dct['table_a']] = rec2.id + [rec.id]
        print('k kw in tree_a Get', k, kw)
        result = super(self.__class__, self).select(*k, **kw)
        #if kw.pop('table', self._dic['table'])==self._dic['_tree_a']: # 是取显示在左下角的已经有关联数据, 需要在Z表取得权限名称. 如果用dbapi里实现left join, 这里就不必要.
        if self.table_az=='table_az': # 是取显示在左下角的已经有关联数据, 需要在Z表取得权限名称. 如果用dbapi里实现left join, 这里就不必要.
            rows = result['rows']
            idz = [i[self.dct['table_z']] for i in rows]
            # rec = getattr(cfg.db1, self.dct['table_z'])(idz)
            name_dic = dict((r.id, r.name) for r in rec)
            #print(name_dic)
            for r in rows:
                r[self.dct['table_z'] + '_name'] = name_dic.get(r[self.dct['table_z']], 'unknown')
        return result

    def insert(self, *k, **kw):
        """自定义Save, 以便正确插入AZ表, 返回结果象destroy"""

        ids = kw.pop('id[]',kw.pop('id'))
        print('k kw @ tree_a: ', k, kw)
        #kw[self._dic['table']] = kw['ida'] = cherrypy.session['ida']
        #kw[self._dic['table_z']] = kw.pop('id[]',[])
        kw['table'] = self.dct['table_az']
        if type(ids)!=type([]):
            ids = [ids]
        for r in ids:
            kw[self.dct['table_z']] = int(r)
            result = super(self.__class__, self).insert(*k, **kw)
        #result = super(self.__class__, self).insert(*k, **kw)
        return dict(success="true")

    def log(self, *k, **kw):
        """本地化log取数, 表要取az表"""

        pass
        #self._dic['table'] = self._dic['table']+'_log'
        super(default, self).log(*k, **kw)

__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])

# $Log: __init__.py,v $
# Revision 1.0  2015-09-25 10:19:30+08  tgm
# Initial revision
