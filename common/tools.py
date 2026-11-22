'''
公共断言工具
'''


def assert_common(result, code=200):
    '''
    公共断言：校验 HTTP 状态码 + 业务 code
    :param result: 接口响应对象
    :param code: 期望的业务 code
    '''
    assert result.status_code == 200, f'HTTP 状态码异常：{result.status_code}'
    data = result.json()
    assert data['code'] == code, f'期望 code={code}，实际={data["code"]}，响应：{data}'
