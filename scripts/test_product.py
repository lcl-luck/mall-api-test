'''
商品模块测试脚本
'''
import pytest

from api.api_product import ApiProduct
from common.read_data import read_data
from common.tools import assert_common

# 读取数据驱动文件
product_data = read_data('product_data.json')


class TestProduct:
    '''商品模块测试类'''

    def test_product_list(self, logged_in_session):
        '''查询商品列表'''
        result = ApiProduct().api_product_list_method(logged_in_session)
        assert_common(result)
        data = result.json()['data']
        assert len(data['list']) > 0, '演示数据里应有商品'
        assert data['total'] > 0

    def test_product_search(self, logged_in_session):
        '''关键字模糊查询
        注意：关键字用「小米」不用「银色」——演示数据里
        「银色星芒」系列 delete_status=1（已删除），接口只查未删除商品
        '''
        result = ApiProduct().api_product_simple_list_method(logged_in_session, keyword='小米')
        assert_common(result)
        items = result.json()['data']
        assert len(items) > 0, '应能搜到小米商品'
        for item in items:
            assert '小米' in item['name'], '返回的商品名都应包含关键字'

    def test_product_detail(self, logged_in_session):
        '''接口关联：模糊查询拿 id → 查详情，断言信息一致'''
        api = ApiProduct()
        result = api.api_product_simple_list_method(logged_in_session, keyword='小米')
        assert_common(result)
        first = result.json()['data'][0]
        detail_result = api.api_product_detail_method(logged_in_session, first['id'])
        assert_common(detail_result)
        assert detail_result.json()['data']['name'] == first['name'], '详情商品名应与查询结果一致'

    def test_product_detail_not_exist(self, logged_in_session):
        '''查不存在的商品 id
        发现点：接口返回 200 + data=null，没按规范返回 404
        '''
        result = ApiProduct().api_product_detail_method(logged_in_session, 999999)
        assert result.json()['code'] == 200
        assert result.json()['data'] is None, '不存在的商品应返回空数据'

    @pytest.mark.parametrize('case', product_data, ids=[c['desc'] for c in product_data])
    def test_product_list_parametrize(self, logged_in_session, case):
        '''数据驱动：不同查询条件组合'''
        result = ApiProduct().api_product_list_method(
            logged_in_session,
            keyword=case.get('keyword'),
            publish_status=case.get('publish_status'),
            page_num=case.get('page_num', 1),
            page_size=case.get('page_size', 5),
        )
        assert_common(result, code=case['expected_code'], http=case.get('expected_http', 200))
        if case.get('expected_empty'):
            assert len(result.json()['data']['list']) == 0, '无结果的查询应返回空列表'
