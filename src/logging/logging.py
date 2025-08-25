import logging
import sqlite3
import os
from datetime import datetime

import config

name_bd = 'logs.db'
filet_name = "logs.txt"

# Получаем путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем родительский каталог (каталог, в котором находится текущий файл)
parent_dir = os.path.dirname(current_file_path)

path_root = os.path.join(parent_dir, '..', '..', name_bd)

# Преобразуем его в абсолютный путь
main_path = os.path.abspath(path_root)

def base_log(mes, i, all):
    print(f"{mes}: {i}/{all}")


def txt_log(mes, i="", all=""):

    # Открываем файл для записи, если файла нет — создаём его
    with open(filet_name, "a") as file:
        if all == "":
            file.write(f"{mes}: {i}" + "\n")
        else:
            file.write(f"{mes}: {i}/{all}" + "\n")


def log_operation(operation, tag1, tag2):
    # Соединяемся с базой данных (если файла нет, он будет создан)
    conn = sqlite3.connect(main_path)
    cursor = conn.cursor()

    # Создаем таблицу, если она не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT,
            tag1 TEXT,
            tag2 TEXT,
            time TEXT
        )
    ''')

    # Получаем текущее время
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Вставляем новую запись
    cursor.execute('''
        INSERT INTO logs (operation, tag1, tag2, time)
        VALUES (?, ?, ?, ?)
    ''', (operation, tag1, tag2, current_time))

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()



def setup_logging():
    handlers = []
    if config.LOG_TO_FILE:
        handlers.append(logging.FileHandler(config.LOG_FILE, encoding="utf-8"))
    if config.LOG_TO_CONSOLE:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format=config.LOG_FORMAT,
        handlers=handlers
    )

    # Отключаем лишний шум
    for noisy in [
        "PIL", "matplotlib", "matplotlib.font_manager",
        "PIL.PngImagePlugin", "sqlalchemy.engine.Engine"
    ]:
        logging.getLogger(noisy).disabled = True

def get_logger():
    return logging.getLogger(__name__)


setup_logging()
LOGGER = get_logger()