#!/usr/bin/env python3
"""
Скрипт принимает путь к CSV-файлу через аргумент командной строки,
читает список пользователей (колонки: name, email, age) и выводит
Использование:
    python user_directory.py <путь_к_csv>
Пример:
    python user_directory.py users.csv
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional


class ExitCode: #numerate-style класс для работы с числовыми кодами ошибок, интуитивно понятные именования вместо цифр
    """Коды завершения программы."""
    SUCCESS = 0
    FILE_NOT_FOUND = 1
    PERMISSION_ERROR = 2
    CSV_ERROR = 3
    MISSING_COLUMNS = 4
    UNKNOWN_ERROR = 5

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Вывод списка пользователей старше 18 лет из CSV.",
        epilog="Файл должен содержать заголовки: name, email, age."
    )
    parser.add_argument(
        "csv_file",
        nargs='?',
        type=str,
        default=None,
        help="Путь к CSV-файлу. Если не указан, будет предложен выбор из файлов в текущей папке."
    )
    return parser.parse_args()


def get_nearly_csv() -> Path:
    # Поиск csv файлов в точке запуска скрипта в случае невведенного пути до конкретного файла
    current_dir = Path.cwd()
    csv_files = list(current_dir.glob("*.csv"))

    if not csv_files:
        print("В текущей папке нет CSV-файлов.", file=sys.stderr)
        sys.exit(ExitCode.FILE_NOT_FOUND)

    print("Найдены следующие CSV-файлы:")
    for i, file_path in enumerate(csv_files, start=1):
        print(f"  {i}. {file_path.name}")

    while True:
        try:
            choice = input("Введите номер файла (или 'q' для выхода): ").strip()
            if choice.lower() == 'q':
                print("Выход по запросу пользователя.")
                sys.exit(ExitCode.SUCCESS)

            idx = int(choice) - 1
            if 0 <= idx < len(csv_files):
                return csv_files[idx]
            else:
                print(f"Пожалуйста, введите число от 1 до {len(csv_files)}.")
        except ValueError:
            print("Некорректный ввод. Введите число или 'q'.")
    

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Вывод списка пользователей старше 18 лет из CSV-файла." \
        " Файл должен содержать заголовки: name, email, age."
    )
    parser.add_argument(
        "csv_file",
        nargs='?',
        type=str,
        default=None,
        help="Путь к CSV-файлу с данными пользователей"
    )
    return parser.parse_args()


def read_users_from_csv(file_path: Path, delimiter: str = ",") -> List[Dict[str, str]]:
    try:
        with open(file_path, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)

            # Проверка наличия обязательных колонок, в случае отсутствия - выбрасывается исключение
            required_columns = {"name", "email", "age"}
            if not required_columns.issubset(reader.fieldnames or []):
                missing = required_columns - set(reader.fieldnames or [])
                raise ValueError(
                    f"Отсутствуют обязательные колонки: {', '.join(missing)}. "
                    f"Заголовки в файле: {reader.fieldnames}"
                )

            users = []
            for row_num, row in enumerate(reader, start=2):  # пропускаем первую строку, т.к. в ней заголовки
                # проверка на пустоту строки
                if not any(row.values()):
                    continue
                users.append(row)
            return users

    except UnicodeDecodeError as e:
        raise csv.Error(
            f"Ошибка декодирования файла. Убедитесь, что файл сохранён в UTF-8.\n{e}"
        ) from e #чейн исключения - csv.Error на базовые e(UnucodeDecodeError)


def filter_adults(users: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    фильтрует юзеров по возрасту
    Входные данные - список пользователей
    Выходные данные - список пользователей старше 18 лет
    """
    adults = []
    for user in users:
        try:
            age_str = user.get("age", "").strip()
            if not age_str:
                print(
                    f"Предупреждение: пропущена строка — пустой возраст для {user.get('name', 'N/A')}",
                    file=sys.stderr
                )
                continue

            age = int(age_str)
            if age > 18:
                user["age_int"] = age
                adults.append(user)
        except ValueError:
            print(
                f"алярм: пропущена строка - некорректный возраст '{user.get('age')}' "
                f"для {user.get('name', 'N/A')}",
                file=sys.stderr
            )
            continue
    return adults


def calculate_column_widths(users: List[Dict[str, str]]) -> Dict[str, int]:
    """
    Вычисляет ширину столбцов для табличного вывода с учётом кириллицы.
    Входные данные - список пользователей.
    Выходные данные - словарь с максимальной шириной для каждого поля.
    """
    widths = {"name": 4, "email": 5, "age": 3}  # минимальная ширина по заголовкам
    for user in users:
        widths["name"] = max(widths["name"], len(user.get("name", "")))
        widths["email"] = max(widths["email"], len(user.get("email", "")))
        # возраст выводится как строка, ширина не больше 3
        widths["age"] = max(widths["age"], len(str(user.get("age", ""))))
    return widths


def print_users_table(users: List[Dict[str, str]]) -> None:
    """
    Печатает таблицу пользователей с динамическим выравниванием.
    """
    if not users:
        print("Нет пользователей старше 18 лет.")
        return
    widths = calculate_column_widths(users)
    # заголовок таблицы
    header = (
        f"{'Name':<{widths['name']}}  "
        f"{'Email':<{widths['email']}}  "
        f"{'Age':>{widths['age']}}"
    )
    separator = "-" * len(header)

    print(header)
    print(separator)

    # Строки данных
    for user in users:
        line = (
            f"{user.get('name', ''):<{widths['name']}}  "
            f"{user.get('email', ''):<{widths['email']}}  "
            f"{user.get('age', ''):>{widths['age']}}"
        )
        print(line)


def main():
    args = parse_arguments()

    if args.csv_file == None:
        csv_path = get_nearly_csv()
        
    else: csv_path = Path(args.csv_file)

    try:
        # Чтение и фильтрация
        all_users = read_users_from_csv(csv_path)
        adults = filter_adults(all_users)

        # Вывод результата
        print_users_table(adults)

        return ExitCode.SUCCESS

    except FileNotFoundError:
        print(f"Ошибка: файл '{csv_path}' не найден.", file=sys.stderr)
        return ExitCode.FILE_NOT_FOUND
    except PermissionError:
        print(f"Ошибка: нет прав для чтения файла '{csv_path}'.", file=sys.stderr)
        return ExitCode.PERMISSION_ERROR
    except csv.Error as e:
        print(f"Ошибка формата CSV: {e}", file=sys.stderr)
        return ExitCode.CSV_ERROR
    except ValueError as e:
        print(f"Ошибка структуры данных: {e}", file=sys.stderr)
        return ExitCode.MISSING_COLUMNS
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        return ExitCode.UNKNOWN_ERROR


if __name__ == "__main__":
    sys.exit(main())