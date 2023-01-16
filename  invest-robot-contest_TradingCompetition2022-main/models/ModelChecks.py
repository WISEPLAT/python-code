from collections import defaultdict


class ModelChecks:
    """ Class store all checks and link to check implement """

    OPEN_LONG = 'open_long'
    OPEN_SHORT = 'open_short'
    CLOSE_LONG = 'close_long'
    CLOSE_SHORT = 'close_short'
    IS_READY = 'is_ready'
    IMPL_METHOD = 'impl_method'

    def __init__(self):
        self._checks = dict(zip((self.OPEN_LONG, self.CLOSE_LONG, self.OPEN_SHORT, self.CLOSE_SHORT),
                                (defaultdict(dict), defaultdict(dict), defaultdict(dict), defaultdict(dict),)))

        # self._check[self._OPEN_LONG]
        # [self._LOW_POINT] = False

    @property
    def checks(self):
        return self._checks

    def add_check(self, group, name, implement_link):
        """ Add new check
        :param
        group -> type of order (_OPEN_LONG, _CLOSE_LONG, etc.)
        name -> name of check
        implement_method -> method which was implemented for checking
        """
        self._checks[group][name][self.IS_READY] = False
        self._checks[group][name][self.IMPL_METHOD] = implement_link
        return self

    def set_ready(self, group, name):
        self._checks[group][name][self.IS_READY] = True

    def __iter__(self):
        self._group_pos = 0
        self._groups = list(self._checks.keys())
        self._group_item_pos = 0
        return self

    def __get_next_no_empty_group_idx__(self, gp_idx):
        gp_idx += 1
        while gp_idx < len(self._groups):
            group_items = self._checks[self._groups[gp_idx]]
            if len(group_items) > 0:
                return gp_idx
            else:
                gp_idx += 1
                continue
        raise StopIteration

    def __next__(self):
        group = self._checks[self._groups[self._group_pos]]
        if self._group_item_pos >= len(group):
            self._group_pos = self.__get_next_no_empty_group_idx__(self._group_pos)
            self._group_item_pos = 0

        if self._group_pos > len(self._groups):
            raise StopIteration

        group_name = self._groups[self._group_pos]
        group_items = self._checks[self._groups[self._group_pos]]
        check_key = list(group_items.keys())
        check_name = check_key[self._group_item_pos]
        item = group_items[check_key[self._group_item_pos]]
        self._group_item_pos += 1
        return group_name, check_name, item
