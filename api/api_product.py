"""
商品管理模块接口
"""
import requests

from config import BASE_URL


class ApiProduct:
    """商品管理模块类"""

    def api_product_list_method(self, session, keyword=None, publish_status=None, page_num=1, page_size=5):
        """
        分页查询商品列表接口方法
        :param session: 已登录的会话（自动携带token）
        :param keyword: 商品名称关键字（可选）
        :param publish_status: 上架状态（可选，1上架 0下架）
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 接口响应对象
        """
        url = f'{BASE_URL}/product/list'
        params = {
            "keyword": keyword,
            "publishStatus": publish_status,
            "pageNum": page_num,
            "pageSize": page_size,
        }
        return session.get(url=url, params=params)

    def api_product_simple_list_method(self, session, keyword=None):
        """
        按名称/货号模糊查询商品简易列表接口方法
        """
        url = f'{BASE_URL}/product/simpleList'
        params = {"keyword": keyword}
        return session.get(url=url, params=params)

    def api_product_detail_method(self, session, product_id):
        """
        根据商品id获取商品编辑信息（详情）接口方法
        """
        url = f'{BASE_URL}/product/updateInfo/{product_id}'
        return session.get(url=url)

    def api_product_create_method(self, session, name=None, product_sn=None, brand_id=None,
                                  product_category_id=None, price=None, original_price=None,
                                  stock=None, delete_status=0):
        """创建商品（JSON 请求体）

        注意：create 未做参数校验（源码无 @Validated），非法数据可能直接入库
        """
        url = f'{BASE_URL}/product/create'
        payload = {
            "name": name,
            "productSn": product_sn,
            "brandId": brand_id,
            "productCategoryId": product_category_id,
            "price": price,
            "originalPrice": original_price,
            "stock": stock,
            "deleteStatus": delete_status,
        }
        return session.post(url=url, json=payload)

    def api_product_update_method(self, session, product_id, name=None, product_sn=None,
                                  price=None, original_price=None, stock=None):
        """更新商品（JSON 请求体），只传要改的字段"""
        url = f'{BASE_URL}/product/update/{product_id}'
        payload = {
            "name": name,
            "productSn": product_sn,
            "price": price,
            "originalPrice": original_price,
            "stock": stock,
        }
        return session.post(url=url, json=payload)

    def api_product_update_publish_status_method(self, session, ids, publish_status):
        """批量上下架商品（表单参数）"""
        url = f'{BASE_URL}/product/update/publishStatus'
        data = {"ids": ','.join(str(i) for i in ids), "publishStatus": publish_status}
        return session.post(url=url, data=data)

    def api_product_update_new_status_method(self, session, ids, new_status):
        """批量设为新品（表单参数）"""
        url = f'{BASE_URL}/product/update/newStatus'
        data = {"ids": ','.join(str(i) for i in ids), "newStatus": new_status}
        return session.post(url=url, data=data)

    def api_product_update_recommend_status_method(self, session, ids, recommend_status):
        """批量推荐商品（表单参数）"""
        url = f'{BASE_URL}/product/update/recommendStatus'
        data = {"ids": ','.join(str(i) for i in ids), "recommendStatus": recommend_status}
        return session.post(url=url, data=data)

    def api_product_update_verify_status_method(self, session, ids, verify_status, detail):
        """批量修改审核状态（表单参数）

        注意：与同组其他接口不同，多一个必传的 detail 参数
        """
        url = f'{BASE_URL}/product/update/verifyStatus'
        data = {
            "ids": ','.join(str(i) for i in ids),
            "verifyStatus": verify_status,
            "detail": detail,
        }
        return session.post(url=url, data=data)

    def api_product_update_delete_status_method(self, session, ids, delete_status):
        """批量修改删除状态（表单参数，逻辑删除：0未删 1已删）"""
        url = f'{BASE_URL}/product/update/deleteStatus'
        data = {"ids": ','.join(str(i) for i in ids), "deleteStatus": delete_status}
        return session.post(url=url, data=data)


if __name__ == '__main__':
    # 自测：创建商品 → 模糊查拿 id → 下架 → 逻辑删除（清理现场）
    from api.api_login import ApiLogin

    s = requests.Session()
    token = ApiLogin().api_login_method().json()['data']['token']
    s.headers['Authorization'] = f'Bearer {token}'

    api_product = ApiProduct()
    print('1 创建商品：', api_product.api_product_create_method(
        s, name='自测商品-可删除', product_sn='AUTO-TEST-001',
        brand_id=1, product_category_id=1, price=9.9, stock=10).json())

    r = api_product.api_product_simple_list_method(s, keyword='自测商品-可删除').json()
    print('2 模糊查询：', r)
    if r['data']:
        product_id = r['data'][0]['id']
        print('3 批量下架：', api_product.api_product_update_publish_status_method(
            s, ids=[product_id], publish_status=0).json())
        print('4 逻辑删除：', api_product.api_product_update_delete_status_method(
            s, ids=[product_id], delete_status=1).json())
    else:
        print('没查到刚建的商品，先看第 1 步返回里有没有报错')
