import argparse

from prod_control import prod_control
from robot_init import reset_robot, init_robot
from services.history_test_data import prepare_history_file
from strategy.robot_engine import start_trade

from sandbox_control import sandbox_control


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--sandbox_control', action="store_true")
    parser.add_argument('--prod_control', action="store_true")
    parser.add_argument('--start_trade', action="store_true")
    parser.add_argument('--reset_robot', action="store_true")
    parser.add_argument('--prepare_history', action="store_true")
    parser.add_argument('--prepare_history_days', type=int)

    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    # инициализация робота: проверка токенов, создание рабочих директорий,
    # однократное скачивание кэша акций в файл data/cache_instruments
    init_robot()

    if args.sandbox_control:
        # запуск программы для управления аккаунтом на сэндбоксе
        sandbox_control()
    elif args.prod_control:
        # запуск программы для управления аккаунтом на проде
        prod_control()
    elif args.reset_robot:
        # очистка всех кэшей и всей истории торговли
        reset_robot()
    elif args.prepare_history:
        # запуск для подготовки файла для тестирования на исторических данных
        prepare_history_file(args.prepare_history_days)
    elif args.start_trade:
        # старт отдельного потока торговли
        start_trade()
