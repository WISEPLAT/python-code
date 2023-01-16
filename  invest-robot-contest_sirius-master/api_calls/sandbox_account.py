import logging

from api_calls.common_requests import make_api_request
from utils.util import pretty_dict

sandbox_service_path = "tinkoff.public.invest.api.contract.v1.SandboxService/"


def get_sandbox_accounts():
    res = make_api_request(sandbox_service_path + 'GetSandboxAccounts')
    logging.debug("Sandbox accounts = {}\n".format(pretty_dict(res)))
    return res


def open_sandbox_account():
    res = make_api_request(sandbox_service_path + 'OpenSandboxAccount')
    logging.debug("Account opened = {}".format(res))
    return res


def close_sandbox_account(account_id):
    res = make_api_request(sandbox_service_path + 'CloseSandboxAccount',
                           dict(accountId=account_id))
    logging.debug("Account closed, AccountId = '{}', res = {}".format(account_id, res))
    return res


def pay_sandbox_account(account_id, currency, units, nano):
    res = make_api_request(sandbox_service_path + 'SandboxPayIn', {
        'accountId': account_id,
        'amount': dict(nano=nano, currency=currency, units=units)
    })
    logging.debug("Pay to account done, AccountId = '{}', res = {}".format(account_id, res))
    return res


def get_sandbox_portfolio(account_id):
    res = make_api_request(sandbox_service_path + 'GetSandboxPortfolio', {
        'accountId': account_id
    })
    logging.debug("Sandbox portfolio for AccountId = '{}':\n{}".format(account_id, pretty_dict(res)))
    return res


def get_sandbox_positions(account_id):
    res = make_api_request(sandbox_service_path + 'GetSandboxPositions', {
        'accountId': account_id
    })
    logging.debug("Sandbox positions for AccountId = '{}':\n{}".format(account_id, pretty_dict(res)))
    return res
