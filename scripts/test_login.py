'''
登录模块测试脚本
'''
from common.read_data import read_data
import pytest
import requests

from common.tools import assert_common
from config import BASE_URL

login_data = read_data('login_data.json')


@pytest.mark.parametrize('case', login_data, ids=[c['desc'] for c in login_data])
def test_api_login_method(case):
    ''' 登录接口'''
    r = requests.post(
        f'{BASE_URL}/admin/login',
        json={'username': case['username'], 'password':case['password']}
    )

    assert_common(r, code=case['expected_code'], msg=case.get('expected_msg'));

    if case['expected_code'] == 200:
        assert r.json()['data']['token']
