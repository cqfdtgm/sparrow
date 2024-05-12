# -*- coding: utf-8 -*-

import os

from .. import default as default_


class default(default_):
    dirs = [os.path.dirname(__file__)] + default_.dirs
    name = 'easyui演示'  # 这个变量如果中间有空格的话, 在easyui tree里, 不能直接作用<a href加的链接, 很奇怪.

    file = __file__

    template_methods = ['default', 'dir']
    setup_methods = ['_download']

    def __init__(self, *k, **kw):
        if len(k):  # 没有多余URL的话，只涉及显示default.html
            path = os.sep.join(self.dirs[0].split(os.sep) + [*k])
            if os.path.isfile(path):  # 如果是jquery源文件，直接下载
                k = ('_download',)
                kw['path'] = path
            else:  # 否则是目录，则显示dir.html
                k = ('dir', *k)
        super(default, self).__init__(*k, **kw)

    def default(self, *k, **kw):
        for _, self.demo_dirs, _ in os.walk(self.dirs[0] + '\\demo', True):
            break  # 巧取一级目录列表，用os.listdir的话要排除文件

    def dir(self, *k, **kw):
        dirs = os.sep.join((self.dirs[0], 'demo', k[0]))
        self.dir = k[0]
        for _, _, self.files in os.walk(dirs):
            break

    def _download(self, path=""):
        """下载文件的方法"""

        yield open(path, "rb").read()


__import__(__name__, {}, {}, [x for x in os.listdir(os.path.dirname(__file__)) if x.count('.') < 1])
