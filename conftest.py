import pytest
import requests
import allure

from api.api_login import ApiLogin


@pytest.fixture
def logged_in_session():
    '''已登录的会话'''
    s = requests.Session()
    token = ApiLogin().api_login_method().json()['data']['token']
    s.headers['Authorization'] = f'Bearer {token}'
    return s

@pytest.fixture(autouse=True)
def _allure_severity(request):
    '''按 desc/用例名自动打 Allure 严重级别 + 中文标题（改节点名实现）'''
    case = request.getfixturevalue('case') if 'case' in request.fixturenames else None
    desc = case.get('desc', '') if isinstance(case, dict) else ''
    name = request.node.name
    doc = request.function.__doc__ or ''

    # 标题中文化：desc 优先 → 文档串 → 还原转义的用例名；改节点名，Allure 跟着显示
    base = desc or (doc.splitlines()[0].strip() if doc else '') \
        or name.encode('ascii', 'backslashreplace').decode('unicode_escape')
    cs = getattr(request.node, 'callspec', None)
    extra = []
    for k, v in (cs.params.items() if cs else []):
        if isinstance(v, (dict, list)):
            continue          # 数据驱动的 case 字典不拼
        if len(str(v)) > 20:
            continue          # 长字符串不拼
        extra.append(f'{k}={v}')
    if extra:
        base = base + f' [{", ".join(extra)}]'
    try:
        request.node.name = base          # 改节点名 → Allure 报告名跟着变
        request.node.originalname = base  # 防 pytest 内部还原
    except Exception:
        pass

    if 'DEFECT' in desc or 'DEFECT' in name or 'DEFECT' in doc:
        allure.dynamic.severity('critical')   # 严重
    elif any(k in desc for k in ('逆向', '反向', '边界', '参数异常', '缺省')):
        allure.dynamic.severity('normal')     # 一般
    else:
        allure.dynamic.severity('minor')      # 轻微
    yield
