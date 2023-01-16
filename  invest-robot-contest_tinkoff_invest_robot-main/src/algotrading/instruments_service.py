from tinkoff.invest import InstrumentIdType

from src.algotrading.utils import api_client_configure


def get_instrument_by(figi: str) -> dict:
    api_client = api_client_configure()

    with api_client as client:
        instrument = client.instruments.get_instrument_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=figi)

    return {'name': instrument.instrument.name,
            'lot': instrument.instrument.lot,
            'currency': instrument.instrument.currency,
            'trading_status': {
                'name': instrument.instrument.trading_status.name,
                'code': instrument.instrument.trading_status.value
                }
            }
