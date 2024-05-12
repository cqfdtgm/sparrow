# -*- coding: utf-8 -*-
# $Header: D:\\RCS\\E\\dragonfly\\0_setup\\0_config\\__init__.py,v 1.0 2015-09-25 10:19:30+08 tgm Exp tgm $

import os

# import cfg

from .. import default
class default(default):
    dirs = [os.path.dirname(__file__)] + default.dirs
    name = 'A-A关系设置'

    def __init__(self, *k, **kw):
        kw.setdefault('_table', 'auth_role')
        super(default, self).__init__(*k, **kw)
        print('self._Kw in a_a', self._kw)
        ##self._dic['_table_var_name'] = '_table_az'
        #cherrypy.session.setdefault('_table_az', 'role_auth')
        #if '_table_az' in kw:  # 通过右上角的"更改目标表"更改了表.
        #    cherrypy.session['_table_az'] = kw.pop('_table_az')
        #self._dic['_table'] = cherrypy.session['_table_az'].split('_')[0]
        # AZ关系表中，真实表名总是字母序在前面。
        #self._dic['_table_az'] = '_'.join(sorted(cherrypy.session['_table_az'].split('_')))
        #self._dic['table_form'] = cherrypy.session['_table_az']
        #self._dic['_table_z'] = cherrypy.session['_table_az'].split('_')[1]
        #if kw.pop('chg','') or '_table' not in kw:    # 如果是通过右上角更改了目标表或是初次进入此页面：
        self.dct['_table'] = table_az = self._kw.pop('_table', 'auth_role')
        #self._dic['_table'] = self._dic['_table_az']
        self.dct['_table_a'], self.dct['_table_z'] = table_az.split('_')
        self.dct['_table_az'] = '_'.join(sorted(table_az.split('_')))
        self._table_az = self._kw.pop('_table_az','_table_a')    # 判断本次Get是取哪个数据 
        self.dct['_real_table'] = self.dct[self._table_az] # 真实表必须更新成为table_a表，以表在表发生chg或是点击上面的菜单切换时，log模板可以正确展示字段 。
        # self.dct['table_kind'] = name

    def Get(self, *k, **kw):
        """自定义Get, 为了增加对q参数的处理"""

        #self._dic['_table'] = self._dic[self._table_az]
        if kw.pop('_log','') == 'true':  # 如果是取日志, 则从az_log表中取.
            kw['_table'] = self.dct['_table_az'] + '_log'
        else:
            kw['_table'] = self.dct.get('_real_table', self.dct['_table'])    # 根据此字段，指定实际取数的表
        if 'notin' in kw: # 对Z端表的排除查询需要用到notin参数, 这样可以避免使用两表join.
            #cherrypy.session['ida'] = kw['notin'] # 要记住上次点击了哪一行
            # 尽量不使用session保存存数据 ， 以便超时后页面还能正常运转。

            kwa = {self.dct['_table_a']:kw.pop('notin')}
            has = getattr(cfg.db15, self.dct['_table_az'])(rows=100, _values_1=False, **kwa)
            has = getattr(has, self.dct['_table_z'])
            #has = list(has)
            if len(has):
                kw['id'] = ['not in', has]
        result = super(default, self).Get(*k, **kw)
        #    return result
        if self._table_az == '_table_az':   # 取的左下角关系表
        #if kw.pop('_table', self._dic['_table']) ==self._dic['_table_az']: # 是取显示在左下角的已经有关联数据, 需要在Z表取得权限名称. 如果用dbapi里实现left join, 这里就不必要.
            rows = result['rows']
            idz = [i[self.dct['_table_z']] for i in rows]
            rec = getattr(cfg.db15, self.dct['_table_z'])(idz)
            name_dic = dict((r.id,r.name) for r in rec)
            for r in rows:
                r[self.dct['_table_z'] + '_name'] = name_dic.get(r[self.dct['_table_z']], '')
        return result
    
    def Destroy(self, *k, **kw):
        """转换id与id[]"""

        print('k, kw', k, kw)
        ids = kw.pop('id[]',kw['id'])
        if type(ids) != type([]):
            ids = [ids]
        print('Destroy')
        for r in ids:
            super(default, self).Destroy(id=int(r), _table=self.dct['_table_az'])
        return dict(success="true")

    def Save(self, *k, **kw):
        """拉截Save请求, 以便正确插入AZ表, 返回结果象destroy一样"""

        #kw[self._dic['_table_z']] = kw['idz'] = kw.pop('id')
        ids = kw.pop('id[]',kw.pop('id',[]))
        kw[self.dct['_table_a']] = kw.pop('ida')
        #kw[self._dic['_table_a']] = kw['ida'] = cherrypy.session['ida']
        kw['_table'] = self.dct['_table_az']
        if type(ids)!=type([]):
            ids = [ids]
        print('A Z AZ, kw', self.dct, kw)
        for r in ids:
            kw[self.dct['_table_z']] = r
            result = super(default, self).Save(*k, **kw)
        return dict(success="true") # 本处Save是当作Destroy使用, 所以需要返回success=true.

    def log(self, *k, **kw):
        """本地化log取数, 表要取az表"""

        self.dct['_real_table'] = self.dct['_table_az'] + '_log'

__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])

# $Log: __init__.py,v $
# Revision 1.0  2015-09-25 10:19:30+08  tgm
# Initial revision
#
