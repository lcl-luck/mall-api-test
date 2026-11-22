'''
登录模块测试脚本
'''
import pytest

from api.api_login import ApiLogin
from common.read_data import read_data
from common.tools import assert_common

login_data = read_data('login_data.json')


@pytest.mark.parametrize('case', login_data, ids=[c['desc'] for c in login_data])
def test_api_login_method(case):
    '''登录接口：正向校验 token，反向校验提示文案'''
    r = ApiLogin().api_login_method(name=case['username'], pwd=case['password'])

    assert_common(r, code=case['expected_code'], msg=case.get('expected_msg'))

    if case['expected_code'] == 200:
        assert r.json()['data']['token'], '登录成功应返回 token'
