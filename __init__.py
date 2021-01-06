import cherrypy
import json
import mako.runtime
import os
import sys

from mako.lookup import TemplateLookup

import sparrows
import tools

mako.runtime.UNDEFINED = 'UNDEFINED'

name = 'homepage'


class default(object):
    exposed = True
    file_ = __file__
    dirs_ = [os.path.dirname(__file__)]
    table_ = 'users'

    json_methods_ = ['select', 'update', 'delete', 'insert', 'tree', 'pop',
                     'directory', 'dnd']
    template_methods_ = ['default', 'login', 'log', 'users', 'debug', 'edit']
    setup_methods_ = ['_test', '_src']

    def __del__(self):
        pass

    def __init__(self, *k, **kw):
        # for multivalues of a varible 'var', cherrypy will change name to 'var[]'
        for key in list(kw.keys()):
            if key.endswith('[]'):
                kw[key[:-2]] = kw.pop(key)
        self._k, self._kw = k, kw
        self._dic = sparrows.dct.copy()
        self._dic['sparrow'] = sparrows
        self._dic['_sess'] = self._sess = sparrows.Session()

    def __iter__(self):
        if not self._k:
            url = cherrypy.request.wsgi_environ['PATH_INFO']
            if not url.endswith('/'):
                raise cherrypy.HTTPRedirect(url + '/')
            self._k = (self.__class__.__name__.split('.')[-1], )
        func: str = self._k[0].lower()
        result = getattr(self, func)(*self._k[1:], **self._kw)
        cherrypy.response.headers['Content-Type'] = 'text/html; charset=utf8'
        if func in self.json_methods_:
            cherrypy.response.headers['Cache-Control'] = 'no-cache'
            cherrypy.response.headers['Expires'] = '0'
            yield json.dumps(result, default=tools.decimal_default)
        elif func in self.template_methods_:
            yield TemplateLookup(self.dirs_).get_template(func + '.html').render(**self._dic)
        elif func in self.setup_methods_:
            yield from result

    def default(self):
        pass

    def directory(self):
        """
        display directory structure on left
        :return: List
        """

        if hasattr(self.__class__, 'directory_'):
            return self.__class__.directory_
        result, tree_dic = [], {}
        for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__)), True):
            packge = '.'.join(root.split(os.path.sep)[1:])
            if '__init__.py' not in files:
                del dirs[:]
                continue
            mod = sys.modules['.'.join(root.split(os.sep)[1:])]
            dic = tree_dic[packge] = dict(children=[], text=getattr(mod, 'name', os.path.basename(root)))
            if root == os.path.dirname(os.path.abspath(__file__)):
                dic['id'] = 1
                dic['url'] = '/login'
                result.append(dic)
                tree_dic['packge'] = result[0]
                continue
            parent = tree_dic['.'.join(root.split(os.path.sep)[1:-1])]
            dic['id'] = parent['id']*10 + len(parent['children']) + 1
            dic['url'] = '/' + '/'.join(root.split(os.sep)[2:]) + '/'
            parent['children'].append(dic)
            if parent['id'] != 1:
                parent['state'] = 'open'
            cherrypy.response.headers['Content-Type'] = 'text/json'
            setattr(self.__class__, 'directory_', result)
            return result

    def login(self):
        pass


# __import__(__name__, {}, {}, [x for x in os.listdir(__name__.replace('.', os.sep)) if x.count('.') < 1])
__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])
