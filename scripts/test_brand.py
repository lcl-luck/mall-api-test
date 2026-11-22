"""
品牌管理模块测试脚本（数据驱动）
"""
import pytest

from api.api_brand import ApiBrand
from common.read_data import read_data
from common.tools import assert_common

# 从数据文件读取反向用例数据
brand_data = read_data('brand_data.json')


def test_brand_create_and_delete(logged_in_session):
    """接口关联全链：创建品牌 → 按名字查回 id → 删除"""
    api = ApiBrand()
    name = '测试品牌链路B'

    # 1. 创建（mall 的创建接口只返回影响行数 1，不返回 id——源码确认过）
    r = api.api_brand_create_method(logged_in_session, name=name, logo='logo.png')
    assert_common(r)
    assert r.json()['data'] == 1, '创建成功应返回影响行数 1'

    # 2. 按名字查回品牌 id（接口关联的关键一步）
    r2 = api.api_brand_list_method(logged_in_session, keyword=name)
    assert_common(r2)
    brand_id = r2.json()['data']['list'][0]['id']

    # 3. 用 id 删除
    r3 = api.api_brand_delete_method(logged_in_session, brand_id)
    assert_common(r3)


def test_brand_list(logged_in_session):
    """正向：分页查询品牌列表"""
    r = ApiBrand().api_brand_list_method(logged_in_session)
    assert_common(r)
    assert len(r.json()['data']['list']) > 0, '演示数据里应有品牌'


@pytest.mark.parametrize('case', brand_data, ids=[c['desc'] for c in brand_data])
def test_brand_create_fail(logged_in_session, case):
    """反向：必填缺失 / 状态值非法（数据从 json 读取）"""
    r = ApiBrand().api_brand_create_method(
        logged_in_session,
        name=case['name'],
        logo=case['logo'],
        factory_status=case['factory_status'],
    )
    assert_common(r, code=case['expected_code'], msg=case.get('expected_msg'))
