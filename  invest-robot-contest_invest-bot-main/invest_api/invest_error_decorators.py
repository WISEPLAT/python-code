import logging

from tinkoff.invest import InvestError, RequestError, AioRequestError

__all__ = ()

logger = logging.getLogger(__name__)


# Method extends logging for Tinkoff api request if it has been failed
def invest_error_logging(func):
    def log_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RequestError as ex:
            tracking_id = ex.metadata.tracking_id if ex.metadata else ""
            logger.error("RequestError tracking_id=%s code=%s repr=%s details=%s",
                         tracking_id, str(ex.code), repr(ex), ex.details)
            raise
        except AioRequestError as ex:
            # tracking_id = ex.metadata.tracking_id if ex.metadata else ""
            logger.error("AioRequestError code=%s repr=%s details=%s",
                         str(ex.code), repr(ex), ex.details)
            raise 
        except InvestError as ex:
            logger.error("InvestError repr=%s", repr(ex))
            raise

    return log_wrapper


# Decorator retries api requests for some kind of exceptions
def invest_api_retry(retry_count: int = 3, exceptions: tuple = ( RequestError )):
    def errors_retry(func):

        def errors_wrapper(*args, **kwargs):
            attempts = 0

            while attempts < retry_count - 1:
                attempts += 1

                try:
                    return func(*args, **kwargs)
                except exceptions:
                    logger.error(f"Retry exception attempt: {attempts}")

            return func(*args, **kwargs)

        return errors_wrapper

    return errors_retry
