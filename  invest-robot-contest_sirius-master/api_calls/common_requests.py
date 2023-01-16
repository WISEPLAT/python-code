import logging

import requests

from utils.settings import settings


# TODO add rate limiter
def make_api_request(path, data=None):
    if data is None:
        data = {}
    token = ''
    if settings()['MAIN']['mode'] == 'history_test':
        token = settings()['SECRETS']['sandbox_token']
    if settings()['MAIN']['mode'] == 'sandbox':
        token = settings()['SECRETS']['sandbox_token']
    if settings()['MAIN']['mode'] == 'prod':
        token = settings()['SECRETS']['prod_token']

    host = settings()['MAIN']['host']
    url = host + path
    logging.debug('Making request, url = {}, data = {}'.format(url, data))
    r = requests.post(url, json=data, headers={'Content-Type': 'application/json',
                                               'Authorization': 'Bearer ' + token,
                                               'Accept': 'application/json',
                                               'x-app-name': settings()['SECRETS']['x-app-name']})
    logging.debug('Status = {}, reason = {}'.format(r.status_code, r.reason))
    logging.debug(r.json())
    return r.json()
