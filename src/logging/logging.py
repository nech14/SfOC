
import sqlite3
import os
from datetime import datetime

name_bd = 'logs.db'

# Получаем путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем родительский каталог (каталог, в котором находится текущий файл)
parent_dir = os.path.dirname(current_file_path)

path_root = os.path.join(parent_dir, '..', '..', name_bd)

# Преобразуем его в абсолютный путь
main_path = os.path.abspath(path_root)

def base_log(mes, i, all):
    print(f"{mes}: {i}/{all}")


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

