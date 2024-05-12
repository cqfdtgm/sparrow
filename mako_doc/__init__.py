# -*- coding: utf-8 -*-

import os

from .. import default as pardefault

class default(pardefault):
    dirs = [os.path.dirname(__file__)] + pardefault.dirs
    name = 'mako文档'  # 这个变量如果中间有空格的话, 在easyui tree里, 不能直接作用<a href加的链接, 很奇怪.


    pass


__import__(__name__, {}, {}, [x for x in os.listdir(os.path.dirname(__file__)) if x.count('.') < 1])
