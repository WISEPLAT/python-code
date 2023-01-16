from tinkoff.invest import Quotation, Client

from settings import settings


def to_float(quotation: Quotation) -> float:
    return quotation.units + quotation.nano / 10 ** 9


def api_client_configure():
    client = Client(settings.api_token,
                    sandbox_token=settings.api_token_sandbox,
                    app_name=settings.app_name)
    return client
