#   -*- coding: utf8    -*-

import os
import sys
import cherrypy

from .. import default as pardefault

name = '系统设置'


class default(pardefault):
    dirs = [os.path.dirname(__file__)] + pardefault.dirs
    file = __file__

    def __init__(self, *k, **kw):
        # print('__init__ @ 0_setup')
        # print('k, kw @ a_setup', k, kw)
        super(default, self).__init__(*k, **kw)


modu = [x for x in os.listdir(__name__.replace('.', os.sep)) if x.count('.') < 1]
print('modus:', __file__, __name__, modu)
__import__(__name__, {}, {}, modu)
# __import__(__name__, {}, {}, [x for x in os.listdir(__name__.replace('.', os.sep)) if x.count('.')<1])
