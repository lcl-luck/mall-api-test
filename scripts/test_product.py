'''商品模块测试脚本'''
from api import api_product
from api.api_product import ApiProduct
from common.read_data import read_data
from common.tools import assert_common

import pytest

product_data = read_data('product_data.json')


class TestProduct:
    '''商品模块测试类'''

    def test_product_list(self, logged_in_session):
        '''测试查询商品列表'''
        result = ApiProduct().api_product_list_method(logged_in_session)

        assert_common(result);
        data = result.json()['data']
        assert len(data['list']) > 0
        assert data['total'] > 0

    def test_product_search(self, logged_in_session):
        result = ApiProduct().api_product_simple_list_method(logged_in_session, '小米')
        assert_common(result);
        items = result.json()['data']
        assert len(items) > 0
        for item in items:
            assert '小米' in item['name']

    def test_product_detail(self, logged_in_session):
        '''模糊查询：用id查详情'''
        api_product = ApiProduct()
        result = api_product.api_product_simple_list_method(logged_in_session, keyword='小米')
        assert_common(result)

        first = result.json()['data'][0]
        product_detail_result = api_product.api_product_detail_method(logged_in_session, first['id'])
        assert_common(product_detail_result)
        assert product_detail_result.json()['data']['name'] == first['name']

    def test_product_detail_not_exist(self, logged_in_session):
        '''查询不存在的商品'''
        result = ApiProduct().api_product_detail_method(logged_in_session, 999999)
        assert result.json()['code'] == 200
        assert result.json()['data'] is None

    @pytest.mark.parametrize('case', product_data, ids = [c['desc'] for c in product_data])
    def test_product_list_parametrize(self, logged_in_session, case):
        result = ApiProduct().api_product_list_method(
            logged_in_session,
            keyword=case['keyword'],
            publish_status=case['publish_status'],
            page_num=case['page_num'],
            page_size=case['page_size']
        )

        assert_common(result, code = case['expected_code'])

        if case.get('expected_empty'):
            assert len(result.json()['data']['list']) == 0