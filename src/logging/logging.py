import logging
import sqlite3
import os
from datetime import datetime

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
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("app.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    logging.getLogger("PIL").disabled = True
    logging.getLogger("matplotlib").disabled = True
    logging.getLogger("matplotlib.font_manager").disabled = True
    logging.getLogger("PIL.PngImagePlugin").disabled = True
    logging.getLogger("sqlalchemy.engine.Engine").disabled = True

def get_logger():
    return logging.getLogger(__name__)