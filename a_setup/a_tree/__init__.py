# -*- coding: utf-8 -*-
# $Header: D:\\RCS\\E\\dragonfly\\0_setup\\0_config\\__init__.py,v 1.0 2015-09-25 10:19:30+08 tgm Exp tgm $

import cherrypy
import os
# import cfg
from .. import default as pardefault


class default(pardefault):
    dirs = [os.path.dirname(__file__)] + pardefault.dirs
    file = __file__

    name = 'A-T关系设置'

    def __init__(self, *k, **kw):
        kw.setdefault('_table', 'users_org')
        super(self.__class__, self).__init__(*k, **kw)
        self.dct.setdefault('_table_atree_add1', '可重复')
        """self._dic['_table_var_name'] = '_table_atree'
        cherrypy.session.setdefault('_table_atree', 'users_org')
        """
        """
        # self._dic['_table'] = cherrypy.session['_table_atree'].split('_')[0] 
        # self._dic['_table_atree'] = '_'.join(sorted(cherrypy.session['_table_atree'].split('_')))
        # self._dic['table_form'] = cherrypy.session['_table_atree']
        # self._dic['_table_z'] = cherrypy.session['_table_atree'].split('_')[1] 
        """
        print('K, KW', k, kw)
        self.dct['_table'] = table_az = self._kw.pop('_table', 'users_org')
        self.dct['_at_add1'] = cfg.dic_add1[table_az]
        self.dct['_table_a'], self.dct['_table_z'] = table_az.split('_')
        self.dct['_table_az'] = '_'.join(sorted(table_az.split('_')))
        self._table_az = self._kw.pop('_table_az', '_table_a')
        self.dct['_real_table'] = self.dct[self._table_az]
        self.dct['table_kind'] = name

    def tree(self, *k, **kw):
        """自定义Tree, 需要将限定条件传给上层Tree"""

        if 'id' in kw:  # 点击展开的情况下, 都不是需要增加或删除操作的.
            kw.pop('delid',0)
            kw.pop('addid',0)
        if 'delid' in kw:   # 如果有delid参数, 参要先做删除操作.
            self.Destroy(id=kw.pop('delid'), *k, **kw)  
        if 'addid' in kw:   # 如果有addid参数, 则要先做增加操作.
            self.Save(id=kw.pop('addid'))
        notin = kw.pop('notin', 'false')
        tb = getattr(cfg.db1, self.dct['_table_az'])
        if self.dct['_table'] in kw:
            cherrypy.session['atree_aid'] = kw[self.dct['_table']] # 记住上次点击了哪笔a端记录.
        kw_a = {self.dct['_table_a']:kw[self.dct['_table_a']], 'rows':-1, '_values_1':False}
        ids = tb(**kw_a).__getattr__(self.dct['_table_z']) # 先取得已包含的节点id列表.
        print('ids 已包含', ids)
        if notin=='true':   # 如果是选不需要的, 则先排除, 然后取结果.
            kw_n = {'rows':-1, '_values_1':False}
            if len(ids):
                kw_n['id'] = ['not in', ids]
            ids = getattr(cfg.db1, self.dct['_table_z'])(**kw_n).id
            print('不包含 in ', ids)
        recs = getattr(cfg.db1, self.dct['_table_z'])(id=ids, rows=-1, order='path', _values_1=False)
        paths = '.'.join(recs.path).split('.')
        if paths[0] == '':
            paths = []
        print('paths', paths)
        new_ids = ids + [int(i) for i in paths]
        new_ids= list(set(new_ids))
        kw['ids'] = ids
        kw['_table'] = self.dct['_table_z']    # atree中需要调用Tree时,总是z表.
        kw['new_ids'] = new_ids
        kw.setdefault('depth',-1)
        result = super(self.__class__, self).Tree(*k, **kw)
        #print('Result: ', result)
        return result

    def delelte(self, *k, **kw):
        """自定义删删除操作, 需要根据id, 从session中取a端id"""

        kw['id'] = kw.pop('id[]',kw['id'])
        ids = kw.pop('id')
        #kw[self._dic['_table']] = cherrypy.session['atree_aid']
        kw[self.dct['_table_z']] = ids
        #kw['_table'] = self._dic['_table_az']
        kw['_values_1'] = False
        tb = getattr(cfg.db1, self.dct['_table_az'])
        rec = tb(**kw)
        print('待删除记录', len(rec), rec.id, rec.__dict__, kw)
        if not len(rec):    #仍然发生待删除记录为0的情况.
            print('error')
            raise
            return dict(error='true')
        kw = {'_table':self.dct['_table_az']}
        for did in rec.id:
            result = super(self.__class__, self).Destroy(id=did, *k, **kw)
        #print('Result', result)
        return result

    def insert(self, *k, **kw):
        """自定义保存操作, 需要需要保存的session中的a端id"""

        print('k kw @ a_tree', k, kw)
        kw['id'] = kw.pop('id[]',kw['id'])
        #kw[self._dic['_table']] = kw.pop('ida')
        #kw[self._dic['_table_z']] = ids
        ids = kw.pop('id')
        if type(ids)!=type([]):
            ids = [ids]
        kw['_table'] = self.dct['_table_az']
        if self.dct['_at_add1'] == '不可重复':
            if len(ids)>1:
                return dict(success='false')
            rec = getattr(cfg.db1,kw['_table'])(ids)
            if len(rec):
                return dict(success="false")
        for aad in ids:
            kw[self.dct['_table_z']] = aad
            print(k, kw)
            result = super(self.__class__, self).Save(*k, **kw)
        return dict(success="true")

    def select(self, *k, **kw):
        """自定义Get, 为了增加对q参数的处理"""

        if kw.pop('_log','') == 'true':
            kw['_table'] = self.dct['_table_az'] + '_log'
        else:
            kw['_table'] = self.dct.get('_real_table', self.dct['_table'])
        if 'q' in kw:
            kwq = kw.pop('q')
            if kwq.encode().isalpha():   # 是字母, 则对config_tables按表名称模糊查询
                kw['name'] = '%'+kwq+'%'
            else:
                kw['name_zh'] = '%' + kwq+'%'   # 否则按中文名
        return super(self.__class__, self).Get(*k, **kw)

    def log(self, *k, **kw):
        
        pass
        self.dct['_real_table'] = self.dct['_table_az'] + '_log'


__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])

# $Log: __init__.py,v $
# Revision 1.0  2015-09-25 10:19:30+08  tgm
# Initial revision
#
