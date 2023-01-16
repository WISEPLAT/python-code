import csv

from utils.parse_util import parse_date

# проверяет корректность файлов с историческими данными на основе последовательности даты-времени
# в случае ошибки будет выведена строка, с которой начинается сбой последовательности
if __name__ == "__main__":
    prev_time = None

    file_paths = [
        "./../data/USD000UTSTOM-20220520.csv",
        "./../data/SBER-20220520.csv",
        "./../data/GAZP-20220520.csv"
    ]

    for file_path in file_paths:
        with open(file_path, newline='') as file:
            reader = csv.DictReader(file, delimiter=",")
            for row in reader:
                current_price = float(row["price"])
                time = parse_date(row["time"])

                if prev_time is None:
                    prev_time = time

                if time < prev_time:
                    print(file_path, row)

                prev_time = time
