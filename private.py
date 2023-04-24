#!  -*- coding:utf8 -*-
# 本文件存放与项目强相关的信息，比如服务器地址，用户名密码，特定系统中使用到的URL等。一般地，本文件应加入.gitignore，以避免上传到互联网上

import os
from . import dbapi

# 行云数据库配置参数，不加入GIT上传清单
#   con_str = """host:port/dbname username password"""
conn_xy = "cirrodata", "cirrordata:1803/BONC XC330001 H8646#r0"
conn_pg15 = "postgresql", "host=localhost port=10123 user=postgres password=DRAGONFLY dbname=xc330001"
conn_sqlite_1 = "sqlite3", "test.sqlite3"


# 根据手机号码获取姓名和单位等信息的URL
showperson_url = "http://oa:7001/directory/showpersons.jsp?mobile="


def init():
    """初始化本项目需要用到的表，SQL语句放在根目录init_sql下面"""

    init_sql = os.sep.join([os.path.dirname(os.path.abspath(__file__)), 'init_sql'])
    for cs in (conn_pg15, conn_sqlite_1):
        db = dbapi.init(*cs)
        if cs[0] == 'postgresql':
            db.autocommit()
        for f in os.listdir(os.sep.join([init_sql, cs[0]])):
            db.execute(open(os.sep.join([init_sql, cs[0], f])).read())
            # db._commit()


print('__name__ of private:', __name__)


if __name__ == '__main__':
    init()
