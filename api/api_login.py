'''
登录模块接口
'''
from config import LOGIN_NAME, PASSWORD, BASE_URL
import requests


class ApiLogin:
    '''登录模块类'''

    def api_login_method(self, name=LOGIN_NAME, pwd=PASSWORD):
        '''
        登录接口方法
        :param name: 账号
        :param pwd: 密码
        :return: 登录接口响应对象
        '''
        url = f'{BASE_URL}/admin/login'

        json = {
            'username': name,
            'password': pwd
        }

        return requests.post(url=url, json=json)

if __name__ == '__main__':
    api_login = ApiLogin()
    result = api_login.api_login_method();
    print(result.json())
