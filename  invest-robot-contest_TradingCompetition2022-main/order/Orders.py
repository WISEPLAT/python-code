class Order:
    """ Class for orders """
    TYPE_LONG_OPEN = "TYPE_LONG_OPEN"
    TYPE_LONG_CLOSE = "TYPE_LONG_CLOSE"

    def __init__(self, order_id, lots_requested, order_type):
        self._order_id = order_id
        self._lots_requested = lots_requested
        self._lots_executed = 0
        self._order_type = order_type
        self._is_order_completed = False

    @property
    def order_id(self):
        return self._order_id

    @property
    def is_order_completed(self):
        """ Check this order is completed"""
        return self._is_order_completed

    @is_order_completed.setter
    def is_order_completed(self, val):
        self._is_order_completed = val

    @property
    def lots_executed(self):
        return self._lots_executed

    @lots_executed.setter
    def lots_executed(self, lots_executed):
        self._lots_executed = lots_executed

    @property
    def order_type(self):
        return self._order_type
