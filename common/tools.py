'''
公共断言工具
'''


def assert_common(result, code=200, msg=None, http=200):
    '''
    公共断言：校验 HTTP 状态码 + 业务 code，msg 不为空时再校验提示文案
    :param result: 接口响应对象
    :param code: 期望的业务 code
    :param msg: 期望的提示文案（包含即可，可选）
    :param http: 期望的 HTTP 状态码（默认 200，固化缺陷用例传实测值）
    '''
    assert result.status_code == http, f'HTTP 状态码异常：{result.status_code}（期望 {http}）'
    data = result.json()
    assert data['code'] == code, f'期望 code={code}，实际={data["code"]}，响应：{data}'
    if msg:
        assert msg in data.get('message', ''), f'提示文案应包含"{msg}"，实际：{data.get("message")}'

