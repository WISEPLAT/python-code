import abc
import importlib.util
import inspect
import sys
from typing import List, Type

from src.containers.config import TraderConfig
from src.containers.market import MarketState, TraderDecision


class BaseTrader(metaclass=abc.ABCMeta):
    _trader_name: str = None

    @classmethod
    @property
    def name(cls):
        return cls._trader_name

    def __init__(self, trader_config: TraderConfig):
        self.trader_config = trader_config

    def initial_message(self):
        return f"Are you sure you want to start the {self.name} trader? (yes/no)"

    @abc.abstractmethod
    async def make_decisions(self, state: MarketState) -> List[TraderDecision]:
        raise NotImplementedError


def load_trader_class(file_name) -> Type[BaseTrader]:
    # find and load the file as a python module
    module_name = f"traders.{file_name}"
    spec = importlib.util.spec_from_file_location(module_name, f"src/traders/{file_name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # find the trader class in the module
    module_classes = inspect.getmembers(module, inspect.isclass)
    trader_cls = next(
        class_
        for _, class_ in module_classes
        if hasattr(class_, "_trader_name") and class_ is not BaseTrader and issubclass(class_, BaseTrader)
    )
    return trader_cls
