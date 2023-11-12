from urllib import parse
import requests

class GASQL:
    def __init__(self, endpoint: str, access_token: str):
        self.endpoint = endpoint
        self.access_token = access_token


    # public api

    def insert(self, table: str, data: dict) -> dict:
        url = self.build_url(self.access_token, type='insert', table=table, columns=list(data.keys()), data=data, where=None)
        return requests.get(url).json()

    def select(self, table: str, where: dict=None) -> dict:
        url = self.build_url(self.access_token, type='select', table=table, columns=None, data=None, where=where)
        return requests.get(url).json()

    def update(self, table: str, data: dict, where: dict=None) -> dict:
        url = self.build_url(self.access_token, type='update', table=table, columns=list(data.keys()), data=data, where=where)
        return requests.get(url).json()

    def delete(self, table: str, where: dict=None) -> dict:
        url = self.build_url(self.access_token, type='delete', table=table, columns=None, data=None, where=where)
        return requests.get(url).json()


    # private utils

    def build_url(self, access_token: str, type: str, table: str, columns: list=None, data: dict=None, where: dict=None):
        params = {
            'a_t': access_token,
            'sql': type,
            'table': table,
        }

        if columns:
            params['cols'] = ','.join(columns)

        if data:
            for key, value in data.items():
                params[key] = value

        if where:
            params['w_col'] = where['w_col']
            params['w_op'] = where['w_op']
            params['w_val'] = where['w_val']

        print(f'{self.endpoint}?{parse.urlencode(params)}')
        return f'{self.endpoint}?{parse.urlencode(params)}'
    
    def where(self, where_data: str):
        w_col, w_op, w_val = where_data.split('')
        return {'w_col': w_col, 'w_op': w_op, 'w_val': w_val}