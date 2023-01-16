from datetime import datetime, timedelta


class SessionCache:
    """ Class Cache session data
    """
    STOCK_AVAILABLE = 'STOCK_AVAILABLE'

    # ToDo ReImplant with using Redis
    _SESSION_CACHE = None

    @classmethod
    def get_session_cache(cls):
        if cls._SESSION_CACHE is None:
            cls._SESSION_CACHE = SessionCache()
            cls._SESSION_CACHE._cache_live_hours = 1  # ToDo Read from config
        return cls._SESSION_CACHE

    def __init__(self):
        self._cache_data = dict()
        self._cache_live_hours = 1

    def cache_data(self, group, key, data):
        if group not in self._cache_data:
            self._cache_data[group] = dict()
        self._cache_data[group][key] = dict(data=data, cached_datetime=datetime.today().now())

    def get_cached(self, group_key, key):
        if group_key in self._cache_data:
            group = self._cache_data[group_key]
            if key in group:
                cached_data = group[key]
                cached_datetime = cached_data['cached_datetime']
                live_time = cached_datetime - timedelta(hours=self._cache_live_hours)
                if cached_datetime <= live_time:
                    return cached_data['data']
        return None
