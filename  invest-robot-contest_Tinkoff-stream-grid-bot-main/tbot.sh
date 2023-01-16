#!/bin/bash
echo "Выберите параметр запуска TBOT:"
echo "1 - Запуск в окружении Docker в режиме демона"
echo "2 - Запуск в окружении Docker"
echo "3 - Запуск в окружении Python"
echo "4 - Создание\обновление контейнера Docker с зависимостями"
echo "5 - Вывод логов контейнера Docker в режиме демона"
echo "6 - Пауза контейнера Docker в режиме демона"
echo "7 - Продолжение работы после паузы контейнера Docker в режиме демона"
echo "8 - Остановка контейнера Docker в режиме демона"
echo "0 - Выход"

read -r action

case $action in
1)
docker run --rm --name tbot -it -d -v $(pwd):/app tbot
;;
2)
docker run --rm --name tbot -it -v $(pwd):/app tbot
;;
3)
python3 tinkoff-stream-grid-bot.py
;;
4)
docker build -t tbot .
;;
5)
docker logs tbot
;;
6)
docker pause tbot
;;
7)
docker unpause tbot
;;
8)
docker stop tbot
;;
0)
echo "Всех благ!"
exit 0
;;
*)
echo "Выберите одно из представленных действий"

esac
