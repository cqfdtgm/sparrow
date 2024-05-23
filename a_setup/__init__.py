#   -*- coding: utf8    -*-

import os
import sys
import cherrypy

from .. import default as pardefault


class default(pardefault):
    dirs = [os.path.dirname(__file__)] + pardefault.dirs
    name = '系统设置'

    file = __file__

    def __init__(self, *k, **kw):
        # print('__init__ @ 0_setup')
        # print('k, kw @ a_setup', k, kw)
        super(default, self).__init__(*k, **kw)

    def select(self, *k, **kw):
        """自定义Get, 为了处理q参数"""

        if 'q' in kw:
            kwq = kw.pop('q')
            if kwq.encode().isalpha():  # 是字母, 则对config_tables按表名查找
                kw['name'] = '%' + kwq + '%'
            else:
                kw['name_zh'] = '%' + kwq + '%'
        return super(default, self).select(*k, **kw)

modu = [x for x in os.listdir(__name__.replace('.', os.sep)) if x.count('.') < 1]
print('modus:', __file__, __name__, modu)
__import__(__name__, {}, {}, modu)
# __import__(__name__, {}, {}, [x for x in os.listdir(__name__.replace('.', os.sep)) if x.count('.')<1])
