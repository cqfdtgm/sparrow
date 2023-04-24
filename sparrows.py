""" doc
"""

import cherrypy
import os
import pickle
import random
import string
import threading

from . import tools

dct = tools.DefaultDict()
dct['charset'] = 'utf8'
dct['title'] = 'sparrow based on cherrypy, mako,sqlite3'
dct['easyui'] = '/js/9_easyui'
dct['cherrypy'] = cherrypy
dct['os'] = os
dct['threading'] = threading


class Session(dict):
    """
    Session of cherrypy
    """
    onlines = {}
    timeout = 60 * 1
    session_file = os.path.dirname(__file__) + os.sep + 'session.dat'

    def __missing__(self, key):
        return '{%s} not exists!' % key

    def __new__(cls, session_id=None):
        """return a session instance, maybe a exists one"""

        if "session_id" not in cherrypy.request.cookie:
            while session_id is None or session_id in cls.onlines:
                session_id = ''.join([random.choice(
                    string.ascii_letters + string.digits) for _ in range(20)])
            sess = super(Session, cls).__new__(cls, session_id)
            sess["session_id"] = session_id
            return sess
        session_id = cherrypy.request.cookie['session_id'].value
        if session_id in cls.onlines:
            return cls.onlines[session_id]
        else:
            sess = super(Session, cls).__new__(cls, session_id)
            sess['session_id'] = session_id
            return sess

    @classmethod
    def load(cls):
        """load sessions data from file"""

        with open(cls.session_file, "rb") as fp:
            try:
                cls.onlines = pickle.load(fp)
            except Exception:
                cls.onlines = {}


dct['onlines'] = Session.onlines
