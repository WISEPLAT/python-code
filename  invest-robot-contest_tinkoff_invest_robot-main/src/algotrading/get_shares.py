from loguru import logger
from tinkoff.invest import InstrumentStatus

from . import glossary, utils


def get_shares(client):
    shares_info = {}
    shares = client.instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE)
    for share in shares.instruments:
        shares_info[share.figi] = {}
        for key in glossary.thead.keys():
            if key == "min_price_increment":
                shares_info[share.figi][key] = utils.to_float(share.__getattribute__(key))
            elif key == "trading_status":
                shares_info[share.figi][key] = glossary.trading_status.get(share.__getattribute__(key)._name_)
            else:
                shares_info[share.figi][key] = share.__getattribute__(key)

    return shares_info


def main():
    api_client = utils.api_client_configure()
    with api_client as client:
        shares = get_shares(client)

    return shares


if __name__ == "__main__":
    main()
