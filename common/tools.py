'''
公共工具模块
'''

def assert_common(result, code = 200, msg = None):
    '''
    公共断言方法：校验业务码（和可选的提示信息）
    :param result: 接口响应对象（requests 和 response）
    :param code: 期望的业务码，默认 200
    :param msg: 期望的提示信息（不传则不校验这一项）
    '''
    result = result.json()
    assert result['code'] == code, f'期望 code={code}，实际={result['code']}，响应：{result}'

    if msg is not None:
        assert result['message'] == msg, f'期望message = {msg!r}，实际={result["message"]!r}'
        