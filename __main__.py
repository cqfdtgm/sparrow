#!python
#   -*- coding: utf8    -*-

import cherrypy
import os
import sys

if __name__ == '__main__':
    conf = os.path.abspath(__file__)[:-2] + 'cfg'
    fp = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(fp))
    root = __import__(os.path.basename(fp))
    cherrypy.quickstart(root, config=conf)
