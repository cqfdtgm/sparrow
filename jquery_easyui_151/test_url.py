import requests
import os
import pytest

from ..test_url import baseurl

curdir = os.path.dirname(__file__)

for _, dirs, _ in os.walk(curdir + '\\demo', True):
    break   # 巧取demo下面的目录列表


def test_url():
    r = requests.get(baseurl + 'jquery_easyui_151/')
    assert r.status_code == 200


@pytest.mark.parametrize("dir", dirs)
def test_dir(dir):
    r = requests.get(baseurl + 'jquery_easyui_151/' + dir)
    assert r.status_code == 200
    dirs_ = os.sep.join((curdir, 'demo', dir))
    for _, _, files_ in os.walk(dirs_):
        break
    for f in files_:
        r = requests.get(baseurl + 'jquery_easyui_151/demo/' + dir + '/' + f)
        assert r.status_code == 200
