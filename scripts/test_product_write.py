"""
商品写接口测试脚本
A 组：批量改状态（publishStatus 全量，其余抽测，deleteStatus 补差异）
B 组：创建/修改（正向闭环 + 反向数据驱动）
"""
import pytest

from api.api_product import ApiProduct
from common.read_data import read_data
from common.tools import assert_common

# 数据驱动文件（B 组反向）
product_write_data = read_data('product_write_data.json')


def _create_one(session, name):
    """造数辅助：建个测试商品并返回 id"""
    api = ApiProduct()
    result = api.api_product_create_method(
        session, name=name, product_sn=name,
        brand_id=1, product_category_id=1, price=1, stock=1)
    assert_common(result)
    items = api.api_product_simple_list_method(session, keyword=name).json()['data']
    return items[0]['id']


def _clean_up(session, product_id):
    """清理辅助：逻辑删除测试商品"""
    ApiProduct().api_product_update_delete_status_method(session, [product_id], 1)


class TestProductStatus:
    """A 组：批量改状态接口"""

    def test_publish_status_flow(self, logged_in_session):
        """1 正向+关联：上架→按状态查回→下架→查不到（流转闭环）"""
        api = ApiProduct()
        pid = _create_one(logged_in_session, '自测-流转')
        assert_common(api.api_product_update_publish_status_method(logged_in_session, [pid], 1))
        data = api.api_product_list_method(logged_in_session, keyword='自测-流转', publish_status=1).json()['data']
        assert any(item['id'] == pid for item in data['list']), '上架后应能按上架状态查到'
        assert_common(api.api_product_update_publish_status_method(logged_in_session, [pid], 0))
        data = api.api_product_list_method(logged_in_session, keyword='自测-流转', publish_status=1).json()['data']
        assert all(item['id'] != pid for item in data['list']), '下架后不应再出现在上架列表'
        _clean_up(logged_in_session, pid)

    def test_publish_status_ids_not_exist(self, logged_in_session):
        """2 反向：ids 不存在 → 影响行数 0 → 操作失败"""
        r = ApiProduct().api_product_update_publish_status_method(logged_in_session, [999999], 0)
        assert r.json()['code'] == 500, '不存在的 id 应返回操作失败'

    def test_publish_status_value_illegal(self, logged_in_session):
        """3 反向：状态值 99
        DEFECT：服务端不校验取值，99 被静默写库（应仅允许 0/1）
        """
        pid = _create_one(logged_in_session, '自测-非法状态')
        r = ApiProduct().api_product_update_publish_status_method(logged_in_session, [pid], 99)
        assert_common(r, code=200)  # DEFECT：未校验状态取值
        _clean_up(logged_in_session, pid)

    def test_publish_status_ids_empty(self, logged_in_session):
        """4 反向：ids 传空
        DEFECT：空 ids 拼出非法 SQL，且把数据库原始报错返回给前端（安全隐患）
        """
        r = ApiProduct().api_product_update_publish_status_method(logged_in_session, [], 0)
        body = r.json()
        assert body['code'] == 500
        assert 'SQL syntax' in body['message'], '空 ids 时前端收到了数据库原始报错'

    def test_new_status_smoke(self, logged_in_session):
        """5 冒烟：设新品→详情查回"""
        api = ApiProduct()
        pid = _create_one(logged_in_session, '自测-新品')
        assert_common(api.api_product_update_new_status_method(logged_in_session, [pid], 1))
        assert api.api_product_detail_method(logged_in_session, pid).json()['data']['newStatus'] == 1
        _clean_up(logged_in_session, pid)

    def test_recommend_status_smoke(self, logged_in_session):
        """6 冒烟：设推荐→详情查回
        注意：返回字段名是 recommandStatus（mall 源码拼写错误），不是 recommendStatus
        """
        api = ApiProduct()
        pid = _create_one(logged_in_session, '自测-推荐')
        assert_common(api.api_product_update_recommend_status_method(logged_in_session, [pid], 1))
        assert api.api_product_detail_method(logged_in_session, pid).json()['data']['recommandStatus'] == 1
        _clean_up(logged_in_session, pid)

    def test_verify_status_smoke(self, logged_in_session):
        """7 冒烟：审核通过→详情查回（此接口需多传 detail）"""
        api = ApiProduct()
        pid = _create_one(logged_in_session, '自测-审核')
        assert_common(api.api_product_update_verify_status_method(logged_in_session, [pid], 1, '测试审核'))
        assert api.api_product_detail_method(logged_in_session, pid).json()['data']['verifyStatus'] == 1
        _clean_up(logged_in_session, pid)

    def test_delete_status_diff(self, logged_in_session):
        """8 差异：逻辑删除后列表查不到"""
        api = ApiProduct()
        pid = _create_one(logged_in_session, '自测-逻辑删')
        assert len(api.api_product_simple_list_method(logged_in_session, keyword='自测-逻辑删').json()['data']) == 1
        assert_common(api.api_product_update_delete_status_method(logged_in_session, [pid], 1))
        assert len(api.api_product_simple_list_method(logged_in_session, keyword='自测-逻辑删').json()['data']) == 0, \
            '逻辑删除后应查不到'


class TestProductCrud:
    """B 组：创建/修改"""

    def test_create_and_delete_loop(self, logged_in_session):
        """9 正向：创建→查回验证字段→逻辑删除（闭环）"""
        api = ApiProduct()
        pid = _create_one(logged_in_session, '自测-闭环')
        detail = api.api_product_detail_method(logged_in_session, pid).json()['data']
        assert detail['name'] == '自测-闭环', '详情名称应与创建一致'
        assert detail['stock'] == 1, '库存应为创建时的值'
        _clean_up(logged_in_session, pid)

    @pytest.mark.parametrize('case', product_write_data, ids=[c['desc'] for c in product_write_data])
    def test_create_parametrize(self, logged_in_session, case):
        """10 反向数据驱动：缺名称/价格负/库存负/市场价负
        价格/库存/市场价 → DEFECT：负数被静默放行入库
        缺名称 → 待实测
        """
        r = ApiProduct().api_product_create_method(
            logged_in_session,
            name=case.get('name'),
            product_sn=case.get('product_sn'),
            brand_id=1,
            product_category_id=1,
            price=case.get('price'),
            original_price=case.get('original_price'),
            stock=case.get('stock'),
        )
        assert_common(r, code=case['expected_code'])

    def test_update_name(self, logged_in_session):
        """11 正向：改名称→查回验证"""
        api = ApiProduct()
        pid = _create_one(logged_in_session, '自测-改名')
        assert_common(api.api_product_update_method(logged_in_session, pid, name='自测-改名-新'))
        assert api.api_product_detail_method(logged_in_session, pid).json()['data']['name'] == '自测-改名-新'
        _clean_up(logged_in_session, pid)

    def test_update_not_exist(self, logged_in_session):
        """12 反向：改不存在的 id
        DEFECT：返回 200 成功，未校验商品是否存在（应报错）
        """
        r = ApiProduct().api_product_update_method(logged_in_session, 999999, name='改不到')
        assert r.json()['code'] == 200  # DEFECT：未校验存在性

    def test_create_product_sn_duplicate(self, logged_in_session):
        """13 反向：productSn 重复
        DEFECT：无唯一性约束，重复货号被放行入库
        """
        pid = _create_one(logged_in_session, '自测-重复sn')
        r = ApiProduct().api_product_create_method(
            logged_in_session, name='自测-重复sn-2', product_sn='自测-重复sn',
            brand_id=1, product_category_id=1, price=1, stock=1)
        assert_common(r, code=200)  # DEFECT：未做唯一性校验
        _clean_up(logged_in_session, pid)
