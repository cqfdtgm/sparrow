import cherrypy
import json
import mako.runtime
import os
import os.path
# import pytest
import sys
import threading

from mako.lookup import TemplateLookup
# from cherrypy.test import helper

from . import dbapi
from . import private
from . import sparrows
from . import tools

mako.runtime.UNDEFINED = 'UNDEFINED'


class default:
    """文档字符串，会详细描述本应用的方法接口，数据库表基本规范字段要求等"""

    exposed = True  #  cherrypy需要以此表示可发布

    charset = 'utf8'    # 网页编码，一般全局不需要改变

    name = '小麻雀'   # 简洁名称，用于在左边菜单中展示，默认会为目录名称

    title = '麻雀虽小，五脏俱全 - 基于cherrypy, mako,sqlite3的透明数据管理系统'   # 网页titile

    easyui = '/js/9_easyui' # easyui脚本URL地址

    file = __file__
    
    """模板搜索路径列表
    默认从本目录开始向上查找，则不需要改变
    dirs[1:]    从上级目录开始向上查找
    dirs[-1]    直接在根目录中查找
    dirs[::-1]  从根目录向下查找
    至于mako文件的继承顺序，则在base.html里进行说明 """
    dirs = [os.path.dirname(__file__)]  # mako的模板搜索路径。子目录会把自己加在这个列表的前面。

    table = 'users'

    setup_methods = ['_test', '_src']       # 系统方法，原样返回
    db_type, connect_str = private.conn_pg15
    db_type, connect_str = private.conn_sqlite_1

    onlines = sparrows.Session.onlines

    cherrypy = cherrypy
    os = os
    threading = threading

    def __del__(self):
        # if 'db' in self.__dict__:
        #    self.db.commit()
        pass

    def __init__(self, *k, **kw):
        # for multivalues of a variable 'var', cherrypy will change name to 'var[]'
        for key in list(kw.keys()):
            if key.endswith('[]'):
                kw[key[:-2]] = kw.pop(key)
                key = key[:-2]
            kw[key.lower()] = kw.pop(key)   # 把所有路径以及关键字转变为小写
        self.k = [i.lower() for i in k]
        self.kw = kw
        # self.dct = sparrows.dct.copy()
        # self.dct['table'] = self.table = kw.pop('table', self.table)
        # self.dct['table_class'] = getattr(self.db, self.dct['table'])
        # self.dct['sparrow'] = sparrows
        # self.dct['_sess'] = self.sess = sparrows.Session()
        self._sess = self.sess = sparrows.Session()
        self.table = self.kw.pop('table', self.table)

    def __iter__(self):
        print('k,kw @ __iter__', self.k, self.kw)
        if not self.k:
            url = cherrypy.request.wsgi_environ['PATH_INFO']
            if not url.endswith('/'):
                raise cherrypy.HTTPRedirect(url + '/')
            self.k = (self.__class__.__name__.split('.')[-1],)
        func = self.k[0].lower()        # 方法统一转为小写
        cherrypy.response.headers['Content-Type'] = 'text/html; charset=utf8'
        if func in self.json_methods:
            result = getattr(self, func)(*self.k[1:], **self.kw)
            cherrypy.response.headers['Cache-Control'] = 'no-cache'
            cherrypy.response.headers['Expires'] = '0'
            yield json.dumps(result, default=tools.decimal_default)
        elif func in self.template_methods:
            # self.dct['table_class'] = getattr(self.db, self.dct['table'])
            # print('dct:', self.dct)
            result = getattr(self, func)(*self.k[1:], **self.kw)
            yield TemplateLookup(self.dirs).get_template(func + '.html').render(this=self)
        elif func in self.setup_methods:
            result = getattr(self, func)(*self.k[1:], **self.kw)
            yield from result

    @staticmethod
    def _src(path=__file__):
        """显示某个文件的源内容，要保留格式。 """

        path = os.sep.join([os.path.dirname(os.path.abspath(__file__)), path])
        s = open(path, "rb").read().decode()
        s = s.replace('<', '&lt;').replace('\t', ' ' * 4)   # 要用于HTML展示的话，小于符号先转义
        yield '<pre>%s</pre>' % s

    @property
    def db(self):
        # 用property的方式实现在访问self.db时，才初始化数据库，部分实现惰性连接
        if '_db' not in self.__dict__:
            print('init db in default...')
            self.__dict__['_db'] = dbapi.init(self.db_type, self.connect_str)
        return self.__dict__['_db']

    # 返回json数据的方法列表，基本都是取自数据库
    json_methods = ['select', 'update', 'delete', 'insert', 'tree', 'pop', 'directory', 'dnd']

    def directory(self):
        """
        display directory structure on left
        :return: List
        """

        if hasattr(self.__class__, 'directory_'):
            return self.__class__.directory_
        result, tree_dic = [], {}
        for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__)), True):
            package = '.'.join(root.split(os.path.sep)[1:])
            if '__init__.py' not in files:
                del dirs[:]
                continue
            mod = sys.modules['.'.join(root.split(os.sep)[1:])]
            dic = tree_dic[package] = dict(children=[], text=mod.default.name)
            if root == os.path.dirname(os.path.abspath(__file__)):
                dic['id'] = 1
                dic['url'] = '/login'
                result.append(dic)
                tree_dic['package'] = result[0]
                continue
            parent = tree_dic['.'.join(root.split(os.path.sep)[1:-1])]
            dic['id'] = parent['id'] * 10 + len(parent['children']) + 1
            dic['url'] = '/' + '/'.join(root.split(os.sep)[2:]) + '/'
            parent['children'].append(dic)
            if parent['id'] != 1:
                parent['state'] = 'open'
        cherrypy.response.headers['Content-Type'] = 'text/json'
        setattr(self.__class__, 'directory_', result)
        return result

    def delete(self, id):
        self.db.delete(self.table, id)
        return dict(success=True)

    def dnd(self, id="", targetid="", point="", max_children=3):
        """
        将树形结构下的一个整体结点，拖动到另一个节点下面
            id: 被移动的节点ID
            targetid: 目标节点
            point: 在目标节点的布放方式， append: 追加作为其第一子节点，bottom: 同级，在其后插入；top:同级，在其前插入
        在tree类表考虑包含path, level字段的情况下，dnd方法相对较复杂。可以从简单入手。
        """

        parentid = targetid if point == 'append' else self.db.select(self.table, id=targetid)['rows'][0]['parentid']
        rec_old = self.db.select(self.table, id=id)['rows'][0]     # 保存原记录的字段值
        if self.db.count(self.table, parentid=parentid) >= max_children and rec_old['parentid'] != parentid:
            return {'isError': True, 'msg': "目标节点下级数量已达限制", 'success': False}
        if point == "append":
            display = self.db.max(self.table, 'display', parentid=targetid) + 1
        else:
            target = self.db.select(self.table, id=targetid)['rows'][0]
            for r in self.db.select(self.table, parentid=target['parentid'], display=['>', target['display']])['rows']:
                # display字段有个隐含BUG: 不停地向上加，时间久远后，有可能某天该字段整数上溢...
                self.db.update(self.table, r['id'], display=r['display'] + 1)
            if point == 'top':  # 搬动目标节点的后续节点后，如果是前插，目标节点的显示顺序也要加1
                display = target['display']
                self.db.update(self.table, targetid, display=target['display'] + 1)
            else:
                display = target['display'] + 1
            targetid = target['parentid']   # 如果不是追加，父节点其实是目标节点的父节点
        self.db.update(self.table, targetid, state='closed')  # 父节点设置为可展开状态。
        self.db.update(self.table, id, parentid=targetid, display=display)
        sons = self.db.count(self.table, parentid=rec_old['parentid'])  # 原父节点如果没有后继了，设置为不可展开状态(open)
        if not sons:
            self.db.update(self.table, rec_old['parentid'], state='open')
        return {"success": True}

    def insert(self, *k, **kw):
        """插入新记录，成功的话，返回新记录的字典"""

        kw.pop('isnewrecord', 'true')  # easyui 的框架在新增时会传这个参数
        new_id = self.db.insert(self.table, **kw)
        res = self.db.select(self.table, id=new_id)
        return res['rows'][0]

    def select(self,  sort="", order="", rows=10, page=1, *k, **kw):
        """获取数据的JSON方法
        以下关键字因为用作参数，不能作为字段名称：rows, page, sort, order, group, table"""

        rows, page = int(rows), int(page)
        if order:    # 要将easyui的order参数，转换为dbapi的order参数
            # easyui的sort: 逗号分隔的字段列表, order: 字段分隔的"asc","desc"列表。
            c = zip(sort.split(','), order.split(','))
            order = ','.join(' '.join(d) for d in c)
        # print('locals @ sparrow.select:', locals())
        result = self.db.select(self.table, order=order, rows=rows, page=page, **kw)
        res = {'rows': result['rows'], 'total': len(result['rows']), 'pagesize': rows, 'pagenumber': page}
        if page > 1 or res['total'] == rows:
            # 并非一页能放完的，需要取真正的总数，以便能显示页数和翻页
            res['total'] = self.db.count(self.table, **kw)
        return res

    def tree(self, id=0, depth=1, rows=3, page=1, **kw):
        """从数据表中取得树形结构的通用方法
        depth: 深度，０表示不递归，n表示递归n层，负数表示递归到底。不递归展开的话，算法简单得多"""

        rows, page = int(rows), int(page)
        kw_l = dict(parentid=id, rows=rows, page=page)
        kw_l['order'] = 'asc'
        kw_l['sort'] = 'display'
        if 'new_ids' in kw:
            kw['id'] = kw['new_ids']    # 限定只在ids集合中取结果
        # ids = kw.get('ids', [])
        recs = self.select(**kw_l)
        if int(recs['total']) > rows:
            return recs
        else:
            return recs['rows']
        """     当需要返回多级树形结构数据时，才会启用下面部分。
        result = []
        for r in recs['rows']:
            if r['id'] in ids:
                r['checkallow'] = True
            else:
                r['checkallow'] = False
                # r['iconCls'] = 'icon-lock'
            result.append(r)
            if depth and r['state'] == 'closed':        # 当需要递归，且当前节点非为叶子节点时
                result[-1]['state'] = 'open'
                kw_t = kw.copy()
                kw_t['rows'] = rows
                kw_t['id'] = r['id']
                kw_t['depth'] = int(depth) - 1
                result[-1]['children'] = default.tree(self, **kw_t)
        return result
        """

    def update(self, id=None, **kw):
        """更新记录，返回更新后的记录的字典"""
        kw.pop('isnewrecord', 'true')  # easyui 的框架在新增时会传这个参数
        self.db.update(self.table, id, **kw)
        return self.db.select(self.table, id=id)['rows'][0]


    # 返回模板内容的方法列表，目录下有同名的html文件
    template_methods = ['default', 'login', 'log', 'users', 'debug', 'edit']
    def debug(self, *k, **kw):
        pass

    def default(self, *k, **kw):
        self.table_class = getattr(self.db, self.table)

    def edit(self, *k, **kw):
        self.table_class = getattr(self.db, self.table)

    def log(self, *k, **kw):
        # 为了不影响其他菜单中的链接，table不加后缀，而是在HTML模板中装载数据的地方加后缀。
        # self.dct['table'] = self.table = kw.pop('table', self.table)
        # self.dct['table_class'] = getattr(self.db, self.table + '_log')
        self.table_class = getattr(self.db, self.table + '_log')

    def login(self, *k, **kw):
        pass

    def users(self, *k, **kw):
        # self.dct['table_class'] = getattr(self.db, self.table)
        self.table_class = getattr(self.db, self.table)


# 在每个包的末尾，手工导入下级各个目录，注意，不导入.py文件，各目录名称也在8个字符以内，不含'.'字符。
__import__(__name__, {}, {}, [x for x in os.listdir(os.path.dirname(os.path.abspath(__file__))) if x.count('.') < 1])
