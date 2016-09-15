#!/usr/bin/env python
'''
Usage:
    eiot.py <INSTANCE_ID> <TOKEN_FILE>

Parameters:

    INSTANCE_ID     the instance id of the user
    TOKEN_FILE      file path to load/store token
'''
import httplib
import json
from docopt import docopt


class EIoTRequestBuilder(object):
    '''
    Basic request builder

    Each type of request should be represented by a single object
    of this class
    '''

    def __init__(self, method, path):
        '''
        :type method: str
        :param method: HTTP method
        :type path: str
        :param path: path template to the API request (w/o common prefix)

        .. example::

            ::

                EIoTRequestBuilder('POST', '/Token/New')
        '''
        self.method = method
        self.path = path

    def get_path(self, elems=None):
        '''
        :type elems: dict
        :param elems: path elements (as defined in the path template)

        :return: path string w/o common prefix

        .. example::

            ::

                builder = EIoTRequestBuilder('GET', '/Module/%{_id}s')
                builder.get_path({'_id': 1})
        '''
        return self.path % elems

    def get_method(self):
        '''
        :return: http method for this request type
        '''
        return self.method

    def is_auth_token(self):
        '''
        :return: True if this method uses AuthToken for authentication
        '''
        return not self.path.startswith('/Token/')


class EIoTCloudRestApiV10(object):
    '''
    REST client for Easy IoT cloud V1.0
    '''

    TOKEN_NEW = EIoTRequestBuilder('POST', '/Token/New')
    TOKEN_LIST = EIoTRequestBuilder('GET', '/Token/List')
    MODULE_NEW = EIoTRequestBuilder('POST', '/Module/New')
    MODULE_LIST = EIoTRequestBuilder('GET', '/Module/List')
    MODULE_GET = EIoTRequestBuilder('GET', '/Module/%(_id)s')
    MODULE_SET_TYPE = EIoTRequestBuilder('POST', '/Module/%(_id)s/Type/%(_value)s')
    MODULE_SET_NAME = EIoTRequestBuilder('POST', '/Module/%(_id)s/Name/%(_value)s')
    PARAM_NEW = EIoTRequestBuilder('POST', '/Module/%(_id)s/NewParameter')
    PARAM_NEW_WITH_NAME = EIoTRequestBuilder('POST', '/Module/%(_id)s/NewParameter/%(_value)s')
    PARAM_GET_BY_NAME = EIoTRequestBuilder('GET', '/Module/%(_id)s/ParameterByName/%(_value)s')
    PARAM_LIST = EIoTRequestBuilder('GET', '/Parameter/List')
    PARAM_GET = EIoTRequestBuilder('GET', '/Parameter/%(_id)s')
    PARAM_SET = EIoTRequestBuilder('POST', '/Parameter/%(_id)s')
    PARAM_SET_NAME = EIoTRequestBuilder('POST', '/Parameter/%(_id)s/Name/%(_value)s')
    PARAM_GET_NAME = EIoTRequestBuilder('GET', '/Parameter/%(_id)s/Name')
    PARAM_SET_DESC = EIoTRequestBuilder('POST', '/Parameter/%(_id)s/Description/%(_value)s')
    PARAM_GET_DESC = EIoTRequestBuilder('GET', '/Parameter/%(_id)s/Description')
    PARAM_SET_UNIT = EIoTRequestBuilder('POST', '/Parameter/%(_id)s/Unit/%(_value)s')
    PARAM_GET_UNIT = EIoTRequestBuilder('GET', '/Parameter/%(_id)s/Unit')
    PARAM_SET_UI_NOTIFY = EIoTRequestBuilder('POST', '/Parameter/%(_id)s/UINotification/%(_value)s')
    PARAM_GET_UI_NOTIFY = EIoTRequestBuilder('GET', '/Parameter/%(_id)s/UINotification')
    PARAM_SET_LOG_TO_DB = EIoTRequestBuilder('POST', '/Parameter/%(_id)s/LogToDatabase/%(_value)s')
    PARAM_GET_LOG_TO_DB = EIoTRequestBuilder('GET', '/Parameter/%(_id)s/LogToDatabase')
    PARAM_SET_AVG_INT = EIoTRequestBuilder('POST', '/Parameter/%(_id)s/AverageInterval/%(_value)s')
    PARAM_GET_AVG_INT = EIoTRequestBuilder('GET', '/Parameter/%(_id)s/AverageInterval')
    PARAM_SET_CHART_STEPS = EIoTRequestBuilder('POST', '/Parameter/%(_id)s/ChartSteps/%(_value)s')
    PARAM_GET_CHART_STEPS = EIoTRequestBuilder('GET', '/Parameter/%(_id)s/ChartSteps')
    PARAM_SET_VALUE = EIoTRequestBuilder('POST', '/Parameter/%(_id)s/Value/%(_value)s')
    PARAM_GET_VALUE = EIoTRequestBuilder('GET', '/Parameter/%(_id)s/Value')
    PARAM_SET_VALUES = EIoTRequestBuilder('POST', '/Parameter/%(_id)s/Values/%(_value)s')
    PARAM_GET_VALUES = EIoTRequestBuilder('GET', '/Parameter/%(_id)s/Values')

    # TODO: PARAM_GET_AVG_INT - check for typo .. see section 3.16
    # http://iot-playground.com/blog/2-uncategorised/78-easyiot-cloud-rest-api-v1-0

    def __init__(self, hostname, instance_id, auth_token_file):
        '''
        :param hostname: cloud server hostname
        :param instance_id: instance id
        :param auth_token_file: filename to load/store token to
        '''
        self.hostname = hostname
        self.instance_id = instance_id
        self.auth_token_file = auth_token_file
        self.auth_token = None
        self.path_prefix = '/RestApi/v1.0'
        self._load_token_from_file()

    def _load_token_from_file(self):
        print('in _load_token_from_file %s' % (self.auth_token_file))
        try:
            token = ''
            with open(self.auth_token_file) as f:
                token = f.read()
            if len(token) != 40:
                raise Exception('len(token) != 40')
            self.set_auth_token(token)
        except Exception as ex:
            print('Could not get token from file %s: %s' % (self.auth_token_file, ex))

    def _store_token_to_file(self, token):
        print('in _store_token_to_file %s %s' % (token, self.auth_token_file))
        try:
            with open(self.auth_token_file, 'wb') as f:
                f.write(token)
        except Exception as ex:
            print('Could not store token to file %s: %s' % (self.auth_token_file, ex))

    def set_auth_token(self, auth_token):
        '''
        :param auth_token: AuthToken of client
        '''
        self.auth_token = auth_token

    def do_rest(self, method, path, headers):
        '''
        Return JSON upon success, raise Exception upon failure.
        '''
        print('[-] API request: %s' % (self.path_prefix + path))
        conn = httplib.HTTPConnection(self.hostname)
        conn.request(method, self.path_prefix + path, headers=headers)
        resp = conn.getresponse()
        if 200 <= resp.status < 300:
            data = resp.read()
            try:
                return json.loads(data)
            except:
                # this issue occurs in MODULE_GET requests...
                return json.loads(data + '}')
        raise Exception(resp.read())

    def do_rest1(self, method, path, headers):
        headers = headers.copy()
        headers['Content-Length'] = 0
        return self.do_rest(method, path, headers)

    def get_auth_headers(self, builder):
        if builder.is_auth_token():
            token = self.get_token()
            headers = {'Eiot-AuthToken': token}
        else:
            headers = {'Eiot-Instance': self.instance_id}
        return headers

    def api_setter_request(self, builder, _id, _value):
        path = builder.get_path({'_id': _id, '_value': _value})
        method = builder.get_method()
        headers = self.get_auth_headers(builder)
        return self.do_rest1(method, path, headers)

    def api_getter_request(self, builder, _id=None):
        path = builder.get_path({'_id': _id})
        method = builder.get_method()
        headers = self.get_auth_headers(builder)
        return self.do_rest1(method, path, headers)

    def get_token(self):
        if self.auth_token is not None:
            return self.auth_token
        else:
            print('We don\'t have a token, requesting from server')
            resp = self.api_getter_request(self.TOKEN_NEW)
            token = resp['Token']
            print('Got a new token from server: %s' % token)
            self._store_token_to_file(token)
            self.set_auth_token(token)
            return self.auth_token


class EIoTClientV10(object):
    '''
    Class for high level operations over the API
    '''

    def __init__(self, api):
        self.api = api

    def get_module_id_by_name(self, module_name):
        '''
        :return: the first module id that corresponds to the name,
            None if there's not match
        '''
        module_list = self.api.api_getter_request(self.api.MODULE_LIST)
        for entry in module_list:
            mid = entry['Id']
            minfo = self.api.api_getter_request(self.api.MODULE_GET, mid)
            if minfo['Name'] == module_name:
                return mid
        return None

    def new_module(self, name=None):
        '''
        Create a new module, possibly with a name

        :param name: name of the new module (default: None)
        :return: module id of the new module
        '''
        mid = self.api.api_setter_request(self.api.MODULE_NEW, None, None)['Id']
        print('EIoTClientV10.new_module - created new module, id: %s' % mid)
        if name is not None:
            print('EIoTClientV10.new_module - setting module name: %s' % name)
            self.api.api_setter_request(self.api.MODULE_SET_NAME, mid, name)
        return mid


def test():
    opts = docopt(__doc__)
    print('[-] Starting test')
    print('[-] Creating API instance')
    api = EIoTCloudRestApiV10('cloud.iot-playground.com:40404', opts['<INSTANCE_ID>'], opts['<TOKEN_FILE>'])
    print('[-] Creating client instance')
    client = EIoTClientV10(api)
    print('[-] Get ID of "Test" module')
    mid = client.get_module_id_by_name('Test')
    if mid is None:
        print('[-] "Test module does not exist, create a new one"')
        mid = client.new_module(name='Test')
    print('[-] Id of "Test" module: %s' % mid)


if __name__ == '__main__':
    test()
