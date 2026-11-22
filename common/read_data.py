'''
公共工具模块：读取测试数据
'''
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def read_data(file_name):
    '''
    读取 data 目录下的 json 测试数据
    :param file_name: 数据文件名
    :return: 数据列表
    '''
    file_path = os.path.join(DATA_DIR, file_name)
    with open(file_path, encoding='utf-8') as f:
        return json.load(f)