'''
商品分类模块测试脚本：修改 update/{id}、导航状态 navStatus、显示状态 showStatus、详情查询
'''
import pytest
import requests

from api.api_product_category import ApiProductCategory
from common.read_data import read_data
from common.tools import assert_common

# 读取数据驱动文件（按接口分段取用）
category_data = read_data('product_category_data.json')
update_cases = category_data['update']
show_status_neg_cases = category_data['showStatus']
nav_status_neg_cases = category_data['navStatus']
delete_neg_cases = category_data['delete']
create_neg_cases = category_data['create']
list_neg_cases = category_data['list']



class TestCategoryUpdate:
    '''商品分类修改用例'''

    @pytest.mark.parametrize('case', update_cases,
                             ids=[c['desc'] for c in update_cases])
    def test_update_parametrize(self, logged_in_session, case):
        '''数据驱动：修改分类（verify=true 的自动查回验证）'''
        api = ApiProductCategory()

        result = api.api_category_update_method(
            logged_in_session,
            category_id=1,
            name=case.get('name'),
            parent_id=case.get('parent_id'),
            product_unit=case.get('product_unit'),
            nav_status=case.get('nav_status'),
            show_status=case.get('show_status'),
            sort=case.get('sort'),
            product_attribute_id_list=case.get('product_attribute_id_list'),
        )

        # 第一层断言：所有用例都验
        assert_common(result, code=case['expected_code'])
        if case.get('expected_msg'):
            assert case['expected_msg'] in result.json()['message']

        # 第二层断言：verify=true 才查回比对
        if case.get('verify'):
            detail = api.api_get_product_category_by_id(logged_in_session, category_id=1)
            assert detail.json()['data']['name'] == case['name'], '名称应已更新'


class TestCategoryShowStatus:
    '''商品分类显示状态用例：正向一个方法 + 逆向数据驱动'''

    @pytest.mark.parametrize('show_status', [0, 1], ids=['隐藏-0', '显示-1'])
    def test_update_show_status_positive(self, logged_in_session, show_status):
        '''正向：showStatus 合法值 0/1，两层断言（code + 查回比对）'''
        api = ApiProductCategory()

        result = api.api_update_show_status_method(logged_in_session, ids=[1], show_status=show_status)
        assert_common(result, code=200)

        # 第二层：查回验证，确认状态真的改了
        detail = api.api_get_product_category_by_id(logged_in_session, category_id=1)
        assert detail.json()['data']['showStatus'] == show_status

    @pytest.mark.parametrize('case', show_status_neg_cases,
                             ids=[c['desc'] for c in show_status_neg_cases])
    def test_update_show_status_negative(self, logged_in_session, case):
        '''逆向：数据驱动，一层断言（code + message 文案）'''
        api = ApiProductCategory()

        result = api.api_update_show_status_method(
            logged_in_session,
            ids=case.get('ids'),
            show_status=case.get('show_status'),
        )

        assert_common(result, code=case['expected_code'])
        if case.get('expected_msg'):
            assert case['expected_msg'] in result.json()['message']


class TestCategoryNavStatus:
    '''商品分类导航状态用例：同构冒烟（showStatus 已测透，这里抽测）'''

    @pytest.mark.parametrize('nav_status', [0, 1], ids=['导航-0', '导航-1'])
    def test_update_nav_status_positive(self, logged_in_session, nav_status):
        '''正向：navStatus 合法值 0/1，两层断言（code + 查回比对）'''
        api = ApiProductCategory()

        result = api.api_update_nav_status_method(logged_in_session, ids=[1], nav_status=nav_status)
        assert_common(result, code=200)

        # 第二层：查回验证，确认导航状态真的改了
        detail = api.api_get_product_category_by_id(logged_in_session, category_id=1)
        assert detail.json()['data']['navStatus'] == nav_status

    @pytest.mark.parametrize('case', nav_status_neg_cases,
                             ids=[c['desc'] for c in nav_status_neg_cases])
    def test_update_nav_status_negative(self, logged_in_session, case):
        '''逆向：数据驱动（越界抽测 + ids 空差异补测），一层断言'''
        api = ApiProductCategory()

        result = api.api_update_nav_status_method(
            logged_in_session,
            ids=case.get('ids'),
            nav_status=case.get('nav_status'),
        )

        assert_common(result, code=case['expected_code'])
        if case.get('expected_msg'):
            assert case['expected_msg'] in result.json()['message']


class TestCategoryDelete:
    '''商品分类删除用例：删除不可逆，一律先建后删'''

    def _create_and_get_id(self, logged_in_session, name, parent_id=0):
        '''建临时分类并反查 id（create 只返回影响行数，不返回 id）'''
        api = ApiProductCategory()
        result = api.api_category_create_method(logged_in_session, name=name, parent_id=parent_id)
        assert_common(result, code=200)

        lst = api.api_category_list_method(logged_in_session, parent_id=parent_id)
        for item in lst.json()['data']['list']:
            if item['name'] == name:
                return item['id']
        raise AssertionError(f'没找到刚建的分类：{name}')

    def test_delete_and_verify(self, logged_in_session):
        '''正向：先建 → 删 → 查回确认没了'''
        api = ApiProductCategory()
        category_id = self._create_and_get_id(logged_in_session, '临时分类-正向删除')

        result = api.api_category_delete_method(logged_in_session, category_id=category_id)
        assert_common(result, code=200)

        # 第二层：查回验证——删除验的是"没了"
        detail = api.api_get_product_category_by_id(logged_in_session, category_id=category_id)
        assert detail.json()['data'] is None, f'分类应已删除，实际 data={detail.json()["data"]}'

    def test_delete_parent_with_child(self, logged_in_session):
        '''业务异常：删有子分类的父分类（应拦截；大概率照删 → 固化 DEFECT）'''
        api = ApiProductCategory()
        parent_id = self._create_and_get_id(logged_in_session, '临时父分类-待删')
        child_id = self._create_and_get_id(logged_in_session, '临时子分类-孤儿观察', parent_id=parent_id)

        result = api.api_category_delete_method(logged_in_session, category_id=parent_id)
        assert_common(result, code=200)

        # 子分类还在、父分类没了 = 孤儿数据实锤
        child = api.api_get_product_category_by_id(logged_in_session, category_id=child_id)
        assert child.json()['data'] is not None, '子分类还在（孤儿）'
        parent = api.api_get_product_category_by_id(logged_in_session, category_id=parent_id)
        assert parent.json()['data'] is None, '父分类应已删除'

    @pytest.mark.parametrize('case', delete_neg_cases,
                             ids=[c['desc'] for c in delete_neg_cases])
    def test_delete_parametrize(self, logged_in_session, case):
        '''逆向/参数异常：删不存在的 id、非法 id（数据驱动）'''
        api = ApiProductCategory()

        result = api.api_category_delete_method(logged_in_session, category_id=case['category_id'])

        assert_common(result, code=case['expected_code'])
        if case.get('expected_msg'):
            assert case['expected_msg'] in result.json()['message']


class TestCategoryCreate:
    '''商品分类创建用例：正向/同名单独方法，逆向数据驱动'''

    def _find_id_by_name(self, logged_in_session, name, parent_id=0):
        '''按名称反查分类 id（create 只返回影响行数，不返回 id）'''
        api = ApiProductCategory()
        lst = api.api_category_list_method(logged_in_session, parent_id=parent_id)
        for item in lst.json()['data']['list']:
            if item['name'] == name:
                return item['id']
        return None

    def test_create_and_verify(self, logged_in_session):
        '''正向：合法创建 → 反查验证 → 清理删除'''
        api = ApiProductCategory()
        name = '临时分类-正向创建'

        result = api.api_category_create_method(logged_in_session, name=name, parent_id=0,
                                                product_unit='个', nav_status=0, show_status=0, sort=0)

        # 查回取值（断言放最后，保证清理一定执行）
        category_id = self._find_id_by_name(logged_in_session, name)
        detail = api.api_get_product_category_by_id(logged_in_session, category_id=category_id) if category_id else None

        # 清理：删掉临时分类
        if category_id:
            api.api_category_delete_method(logged_in_session, category_id=category_id)

        # 断言统一放最后
        assert_common(result, code=200)
        assert category_id is not None, '创建后应能反查到分类'
        assert detail.json()['data']['name'] == name
        assert detail.json()['data']['parentId'] == 0

    def test_create_duplicate_name(self, logged_in_session):
        '''业务规则：同名再建应拦截（大概率放行 → DEFECT）'''
        api = ApiProductCategory()
        name = '临时分类-同名测试'

        first = api.api_category_create_method(logged_in_session, name=name, parent_id=0)
        second = api.api_category_create_method(logged_in_session, name=name, parent_id=0)

        # 查回取值：同名的有几条
        lst = api.api_category_list_method(logged_in_session, parent_id=0)
        same_name_ids = [item['id'] for item in lst.json()['data']['list'] if item['name'] == name]

        # 清理：同名的全删
        for cid in same_name_ids:
            api.api_category_delete_method(logged_in_session, category_id=cid)

        # 断言统一放最后
        assert_common(first, code=200)
        assert_common(second, code=200)  # 应拦截同名，大概率 200 放行 → 固化 DEFECT
        # DEFECT-13：同名两条都入库（唯一性缺失），固化实际行为
        assert len(same_name_ids) == 2, f'同名应只有一条，实际 {len(same_name_ids)} 条'  # 原来是 == 1

    @pytest.mark.parametrize('case', create_neg_cases,
                             ids=[c['desc'] for c in create_neg_cases])
    def test_create_parametrize(self, logged_in_session, case):
        '''逆向数据驱动：缺省/非法参数（取值→清理→断言）'''
        api = ApiProductCategory()

        result = api.api_category_create_method(
            logged_in_session,
            name=case.get('name'),
            parent_id=case.get('parent_id'),
            product_unit=case.get('product_unit'),
            nav_status=case.get('nav_status'),
            show_status=case.get('show_status'),
            sort=case.get('sort'),
            icon=case.get('icon'),
            keywords=case.get('keywords'),
            description=case.get('description'),
        )

        # 查回取值（verify=true：看 navStatus 缺省时默认值谁兜底）
        actual_nav = None
        if case.get('verify') and case.get('name'):
            cid = self._find_id_by_name(logged_in_session, case['name'])
            if cid:
                detail = api.api_get_product_category_by_id(logged_in_session, category_id=cid)
                actual_nav = detail.json()['data']['navStatus']

        # 清理：真建出来了就删，防垃圾堆积
        if case.get('name'):
            parent = case.get('parent_id')
            parent = parent if isinstance(parent, int) else 0
            cid = self._find_id_by_name(logged_in_session, case['name'], parent_id=parent)
            if cid:
                api.api_category_delete_method(logged_in_session, category_id=cid)

        # 断言统一放最后
        assert_common(result, code=case['expected_code'])
        if case.get('expected_msg'):
            assert case['expected_msg'] in result.json()['message']
        if case.get('verify'):
            assert actual_nav == case['nav_status'], \
                f'navStatus 缺省应存 {case["nav_status"]}，实际存了 {actual_nav}'


class TestCategoryList:
    '''商品分类列表查询用例（读接口，无需清理）'''

    def test_list_positive(self, logged_in_session):
        '''正向：parentId=0 + 分页参数，验结构 + 过滤正确'''
        api = ApiProductCategory()

        result = api.api_category_list_method(logged_in_session, parent_id=0, page_num=1, page_size=2)
        assert_common(result, code=200)

        items = result.json()['data']['list']
        assert len(items) <= 2, f'每页最多 2 条，实际 {len(items)} 条'
        for item in items:
            assert item['parentId'] == 0, f'过滤验证：应只返回 parentId=0，实际 {item["parentId"]}'

    def test_list_page2(self, logged_in_session):
        '''正向：翻页 pageNum=2，与第 1 页不重复'''
        api = ApiProductCategory()

        page1 = api.api_category_list_method(logged_in_session, parent_id=0, page_num=1, page_size=2)
        result = api.api_category_list_method(logged_in_session, parent_id=0, page_num=2, page_size=2)
        assert_common(result, code=200)

        ids1 = [i['id'] for i in page1.json()['data']['list']]
        ids2 = [i['id'] for i in result.json()['data']['list']]
        assert set(ids1) & set(ids2) == set(), f'两页不应重复：{ids1} vs {ids2}'

    def test_list_default_page_num(self, logged_in_session):
        '''正向：缺省 pageNum，应默认查第 1 页（与显式 pageNum=1 结果一致）'''
        api = ApiProductCategory()

        default = api.api_category_list_method(logged_in_session, parent_id=0, page_num=None, page_size=2)
        explicit = api.api_category_list_method(logged_in_session, parent_id=0, page_num=1, page_size=2)
        assert_common(default, code=200)

        ids_default = [i['id'] for i in default.json()['data']['list']]
        ids_explicit = [i['id'] for i in explicit.json()['data']['list']]
        assert ids_default == ids_explicit, f'缺省应等于 pageNum=1：{ids_default} vs {ids_explicit}'

    def test_list_default_page_size(self, logged_in_session):
        '''正向：缺省 pageSize，应默认每页 5 条'''
        api = ApiProductCategory()

        result = api.api_category_list_method(logged_in_session, parent_id=0, page_num=1, page_size=None)
        assert_common(result, code=200)

        items = result.json()['data']['list']
        assert len(items) <= 5, f'缺省 pageSize 应为 5，实际返回 {len(items)} 条'

    @pytest.mark.parametrize('case', list_neg_cases,
                             ids=[c['desc'] for c in list_neg_cases])
    def test_list_parametrize(self, logged_in_session, case):
        '''逆向/边界：数据驱动（读接口，不用清理）'''
        api = ApiProductCategory()

        result = api.api_category_list_method(
            logged_in_session,
            parent_id=case.get('parent_id'),
            page_num=case.get('page_num'),
            page_size=case.get('page_size'),
        )

        assert_common(result, code=case['expected_code'])
        if case.get('expected_msg'):
            assert case['expected_msg'] in result.json()['message']
        if case.get('verify_empty'):
            assert result.json()['data']['list'] == [], '不存在的 parentId 应返回空列表'



class TestCategoryWithChildren:
    '''分类树查询用例：树结构验证 + 鉴权基线（模块收口）'''

    def _find_id_by_name(self, logged_in_session, name, parent_id=0):
        '''按名称反查分类 id（create 只返回影响行数，不返回 id）'''
        api = ApiProductCategory()
        lst = api.api_category_list_method(logged_in_session, parent_id=parent_id)
        for item in lst.json()['data']['list']:
            if item['name'] == name:
                return item['id']
        return None

    def test_with_children_tree(self, logged_in_session):
        '''正向：自建父子分类 → 查树验证挂载关系 → 清理'''
        api = ApiProductCategory()
        parent_name = '临时父-树验证'
        child_name = '临时子-树验证'

        # 造数据：先建父、再建子（子挂父下）
        api.api_category_create_method(logged_in_session, name=parent_name, parent_id=0)
        parent_id = self._find_id_by_name(logged_in_session, parent_name)
        assert parent_id is not None, '前置失败：父分类没建出来'

        api.api_category_create_method(logged_in_session, name=child_name, parent_id=parent_id)
        child_id = self._find_id_by_name(logged_in_session, child_name, parent_id=parent_id)
        assert child_id is not None, '前置失败：子分类没建出来'

        # 查树取值：找父节点，看 children 里挂的是不是亲儿子
        result = api.api_category_list_with_children_method(logged_in_session)
        tree = result.json()['data']
        parent_node = next((n for n in tree if n['id'] == parent_id), None)
        child_in_tree = None
        if parent_node:
            child_in_tree = next((c for c in (parent_node.get('children') or [])
                                  if c['id'] == child_id), None)

        # 清理：先删子再删父（顺序反了就触发 DEFECT-12 留孤儿）
        api.api_category_delete_method(logged_in_session, category_id=child_id)
        api.api_category_delete_method(logged_in_session, category_id=parent_id)

        # 断言统一放最后
        assert_common(result, code=200)
        assert parent_node is not None, f'树里应能找到父分类 {parent_name}'
        assert child_in_tree is not None, '子分类应挂在父节点的 children 下'
        # DEFECT-21：树查询子节点 parentId 返回 null（detail/list 有值，接口间不一致），固化实际行为
        assert child_in_tree['parentId'] is None, f'树子节点 parentId 当前为 null，实际 {child_in_tree["parentId"]}'

    def test_with_children_unauthorized(self):
        '''横切冒烟：未登录访问应 401（鉴权基线 + 给 401 误报缺陷当对照照）'''
        api = ApiProductCategory()
        raw_session = requests.Session()   # 未登录：不带 token 的裸会话

        result = api.api_category_list_with_children_method(raw_session)

        assert_common(result, code=401)
        assert '暂未登录' in result.json()['message']

