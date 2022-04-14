# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import json
import time

import requests
from absl import logging

from typing import List


class RequestHelper():
    """
    Makes request to the API easier. Retries on expired tokens et.
    """
    username = None
    password = None
    tokenUrl = None
    token = None
    baseHeader = {'content-type': 'application/json'}
    baseUrl = None

    def __init__(self, username: str = None, password: str = None, tokenUrl: str = None, baseUrl: str = None):
        """

        :param username: Username for the API
        :param password: Password for the User
        :param tokenUrl: Full URL https://example.com/gettokens where authetication tokens can be aquired.
        :param baseUrl: Full baseURL where API endpoints live https://example.com/api/v1/
        """
        if username:
            RequestHelper.username = username
        if password:
            RequestHelper.password = password
        if tokenUrl:
            RequestHelper.tokenUrl = tokenUrl
        if baseUrl:
            RequestHelper.baseUrl = baseUrl

    def getToken(self):
        """
        Queries API for an authentication token and stores it in a class variable.
        :return: No Return
        """
        if not (RequestHelper.username and RequestHelper.password and RequestHelper.tokenUrl):
            raise Exception(
                'Username, Password and TokenURL have to be supplied before an authentication token can be acquired.')

        request = requests.get(RequestHelper.tokenUrl,
                               json={'username': RequestHelper.username, 'password': RequestHelper.password},
                               verify=False)
        if request.status_code != 200:
            raise LookupError(
                "Error {} for request to URL {}. Aborting!".format(request.status_code, RequestHelper.tokenUrl))
        token = request.json()
        RequestHelper.token = 'Bearer {}'.format(token['token'])
        logging.info('Generated new token.')

    def _makeRequest(self, endpoint: str, requestType: str, data: dict = {}, params: dict = {}):
        """
        Make a request of type requestType to the URL. The endpoint is appended to the baseUrl.
        :param endpoint: Endpoint to query. E.g., /shopfloor/
        :param requestType: REST types. Supported values are: get, patch, delete, post
        :param data: Dictionary with data to pass to the request. Must be json serializable.
        :param params: Dictionary with parameters to add to the URL. E.g., params={'machine':3} results in .../?machine=3 at the end of the URL.
        :return: Request object
        """
        assert type(data) is dict, "Data has to be passed as dict type!"

        time.sleep(0.01)

        header = self.baseHeader
        header['Authorization'] = RequestHelper.token

        if requestType == 'get':
            requestFunction = requests.get
        elif requestType == 'patch':
            requestFunction = requests.patch
        elif requestType == 'delete':
            requestFunction = requests.delete
        elif requestType == 'post':
            requestFunction = requests.post
        else:
            raise Exception('Request type {} unknown. Aborting!'.format(requestType))

        requestUrl = joinUrl([self.baseUrl, endpoint])
        request = requestFunction(requestUrl, json=data, verify=False, headers=header, params=params)

        if request.status_code == 403:
            logging.warning(
                "Error {} for request to URL {}. Generating new token an retry!".format(request.status_code, endpoint))
            self.getToken()
            request = self._makeRequest(endpoint=endpoint, requestType=requestType, data=data, params=params)

        if request.status_code > 399:
            raise LookupError("Error {} for request to URL {}. Aborting!".format(request.status_code, requestUrl))

        return request

    def get(self, url: str, data: dict = {}, params: dict = {}):
        request = self._makeRequest(url, requestType='get', data=data, params=params)
        return request

    def delete(self, url: str, data: dict = {}, params: dict = {}):
        request = self._makeRequest(url, requestType='delete', data=data, params=params)
        return request

    def post(self, url: str, data: dict = {}, params: dict = {}):
        request = self._makeRequest(url, requestType='post', data=data, params=params)
        return request

    def patch(self, url: str, data: dict = {}, params: dict = {}):
        request = self._makeRequest(url, requestType='patch', data=data, params=params)
        return request


def createOrPatch(endpoint: List[str], data: dict, checkfor: str=None):
    """
    Checks if an entry is present in the api and otherwise creates it.

    :param endpoint: Endpoint to query. E.g., ['shopfloor']. BaseURL is provided in Requesthelper
    :param data: Dictionary with data to pass to the endpoint.
    :param checkfor: Key of an element in data which makes the entry unique. E.g. 'name'
    :return: Request in JSON format
    """
    if checkfor:
        assert checkfor in data

    rH = RequestHelper()
    endpoint = joinUrl(endpoint)

    if checkfor:
        request = rH.get(endpoint, params={checkfor: data[checkfor]}).json()

        if request['count'] > 1:
            raise LookupError(
                "Error multiple responses for request to URL {}. Multiple entries with the same name present!".format(endpoint))

        if request['count'] == 1:
            logging.info("Object found for {} - Patching!".format(endpoint))
            request = rH.patch(joinUrl([endpoint, request['results'][0]['id']]), data)
            return request.json()

    logging.info("Object not found for {} - Creating!".format(endpoint))
    request = rH.post(endpoint, data)

    return request.json()


def checkAndDelete(url: List[str]):
    """
    Checks if an entry in the api exists and deletes it.
    :param url: E.g. ['shopfloor','3'] tries to delete .../shopfloor/3/
    :return: Empty dictionary on success else, the request as json.
    """
    rH = RequestHelper()
    url = joinUrl(url)

    request = rH.get(url)

    if "count" in request:
        raise OverflowError(
            "Error for delete request to URL {} - Too many objects found. Aborting!".format(request.status_code, url))

    request = rH.delete(url=url)

    resp = json.dumps({})
    if request.status_code != 204:
        resp = request.json()

    return resp


def joinUrl(urlPart_list: List[str]) -> str:
    """
    Join different parts to a URL.

    :param urlPart_list: differnt parts of a url to join.
    :return: Joined URL as a string
    """
    assert len(urlPart_list) > 0

    joinedUrl = urlPart_list[0]

    for urlPart in urlPart_list[1:]:
        urlPart = str(urlPart)
        while len(joinedUrl) > 0 and joinedUrl[-1] == '/':
            joinedUrl = joinedUrl[:-1]
        while urlPart[0] == '/' and len(urlPart) > 0:
            urlPart = urlPart[1:]
        while urlPart[-1] == '/' and len(urlPart) > 0:
            urlPart = urlPart[:-1]

        joinedUrl = joinedUrl + '/' + urlPart

    return joinedUrl + '/'
