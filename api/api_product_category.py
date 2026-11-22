'''
商品分类模块接口
'''
import requests

from config import BASE_URL


class ApiProductCategory:
    '''商品分类模块类'''

    def api_category_update_method(self, session, category_id, name=None, parent_id=0,
                                   product_unit=None, nav_status=0, show_status=0,
                                   sort=0, icon=None, keywords=None,
                                   description=None, product_attribute_id_list=None):
        '''
        修改商品分类方法
        :param session: 已登录的会话
        :param category_id: 分类 id（URL 路径）
        :param name: 分类名称（后端 @NotEmpty 必填）
        :param parent_id: 父分类 id，0 表示一级
        :param product_attribute_id_list: 关联商品属性 id 列表，传空列表=清空
        :return: 接口响应对象
        '''
        url = f'{BASE_URL}/productCategory/update/{category_id}'
        payload = {
            "parentId": parent_id,
            "name": name,
            "productUnit": product_unit,
            "navStatus": nav_status,
            "showStatus": show_status,
            "sort": sort,
            "icon": icon,
            "keywords": keywords,
            "description": description,
            "productAttributeIdList": product_attribute_id_list,
        }
        return session.post(url, json=payload)

    def api_update_nav_status_method(self, session, ids, nav_status):
        '''
        批量修改导航栏显示状态（表单参数接口，不是 JSON）
        :param session: 已登录的会话
        :param ids: 分类 id 列表
        :param nav_status: 导航栏显示状态
        :return: 接口响应对象
        '''
        url = f'{BASE_URL}/productCategory/update/navStatus'
        data = {
            'ids': ','.join(str(i) for i in ids),
            'navStatus': nav_status
        }
        return session.post(url, data=data)

    def api_update_show_status_method(self, session, ids, show_status):
        '''
        批量修改显示状态（表单参数接口，不是 JSON）
        :param session: 已登录的会话
        :param ids: 分类 id 列表
        :param show_status: 显示状态
        :return: 接口响应对象
        '''
        url = f'{BASE_URL}/productCategory/update/showStatus'
        data = {
            'ids': ','.join(str(i) for i in ids),
            'showStatus': show_status
        }
        return session.post(url, data=data)

    def api_get_product_category_by_id(self, session, category_id):
        '''
        通过商品分类的id获取商品分类的详细信息
        :param session: 已登录的会话
        :param category_id: 商品分类的 id
        :return: 根据商品分类id查商品分类的响应结果
        '''
        url = f'{BASE_URL}/productCategory/{category_id}'
        return session.get(url)

    def api_category_create_method(self, session, name, parent_id=0, product_unit=None,
                                   nav_status=0, show_status=0, sort=0, icon=None,
                                   keywords=None, description=None):
        '''
        创建商品分类（给"先建后删"用例造数据）
        :param session: 已登录的会话
        :param name: 分类名称
        :param parent_id: 父分类 id，0 表示一级分类
        :return: 接口响应对象
        注意：后端返回影响行数，不是新分类 id，id 要用 list 反查
        '''
        url = f'{BASE_URL}/productCategory/create'
        payload = {
            "parentId": parent_id,
            "name": name,
            "productUnit": product_unit,
            "navStatus": nav_status,
            "showStatus": show_status,
            "sort": sort,
            "icon": icon,
            "keywords": keywords,
            "description": description,
        }
        return session.post(url, json=payload)

    def api_category_delete_method(self, session, category_id):
        '''
        删除商品分类
        :param session: 已登录的会话
        :param category_id: 分类 id（URL 路径）
        :return: 接口响应对象
        注意：后端删之前不校验子分类/商品，有子分类也照删（已知缺陷）
        '''
        url = f'{BASE_URL}/productCategory/delete/{category_id}'
        return session.post(url)

    def api_category_list_method(self, session, parent_id=0, page_num=1, page_size=50):
        '''
        分页查询某父分类下的子分类（用于反查新建分类的 id）
        :param session: 已登录的会话
        :param parent_id: 父分类 id，0 表示一级分类列表
        :param page_num: 页码，传 None 表示不带该参数（验默认值用）
        :param page_size: 每页条数，传 None 表示不带该参数（验默认值用）
        :return: 接口响应对象
        '''
        url = f'{BASE_URL}/productCategory/list/{parent_id}'
        params = {}
        if page_num is not None:
            params['pageNum'] = page_num
        if page_size is not None:
            params['pageSize'] = page_size
        return session.get(url, params=params)

    def api_category_list_with_children_method(self, session):
        '''
        查询所有分类（树形结构，父分类嵌套子分类）
        :param session: 会话（已登录/未登录均可，未登录用于鉴权基线用例）
        :return: 接口响应对象
        '''
        url = f'{BASE_URL}/productCategory/list/withChildren'
        return session.get(url)
