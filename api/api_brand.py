"""
品牌管理模块接口
"""
import requests

from config import BASE_URL


class ApiBrand:
    """品牌管理模块类"""

    def api_brand_create_method(self, session, name, logo, factory_status=0, show_status=1):
        """
        添加品牌接口方法
        :param session: 已登录的会话（自动携带token）
        :param name: 品牌名称（必填）
        :param logo: 品牌logo（必填，任意字符串即可）
        :param factory_status: 是否厂家（只能0或1）
        :param show_status: 是否显示（只能0或1）
        :return: 接口响应对象
        """
        url = f'{BASE_URL}/brand/create'
        json = {
            "name": name,
            "logo": logo,
            "factoryStatus": factory_status,
            "showStatus": show_status,
        }
        return session.post(url=url, json=json)

    def api_brand_list_method(self, session, keyword=None, page_num=1, page_size=10):
        """
        分页查询品牌列表接口方法
        """
        url = f'{BASE_URL}/brand/list'
        params = {
            "keyword": keyword,
            "pageNum": page_num,
            "pageSize": page_size,
        }
        return session.get(url=url, params=params)

    def api_brand_delete_method(self, session, brand_id):
        """
        删除品牌接口方法
        """
        url = f'{BASE_URL}/brand/delete/{brand_id}'
        return session.get(url=url)


if __name__ == '__main__':
    # 调试当前脚本：先登录，再调品牌接口
    from api.api_login import ApiLogin

    s = requests.Session()
    token = ApiLogin().api_login_method().json()['data']['token']
    s.headers['Authorization'] = f'Bearer {token}'

    api_brand = ApiBrand()
    print('添加品牌：', api_brand.api_brand_create_method(s, name='测试品牌A', logo='logo.png').json())
    print('查品牌列表：', api_brand.api_brand_list_method(s).json())
