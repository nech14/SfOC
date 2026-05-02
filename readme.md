# SoOC

## 📌 Описание

**SoOC** — это сервис для первичной обработки изображений с камер всего неба (all-sky cameras).

Ключевая особенность проекта — **pipeline-архитектура обработки изображений**, где каждое преобразование представлено как отдельный шаг (*step*).

---

## 🧠 Архитектура

В основе SoOC лежит модульная система обработки:

### 🔹 Step (шаг обработки)
Каждая операция — это независимый шаг:
- вычитание dark frame
- удаление шумов
- применение корректирующей матрицы
- маскирование
- нормализация / перевод в Rayleigh

Шаги можно комбинировать.

---

### 🔹 Pipeline
Pipeline — это последовательность шагов, применяемых к изображению.

Пример pipeline:

```
Load → Dark subtraction → Noise filtering → Mask → Calibration → Visualization
```

В проекте используются **преднастроенные pipeline**, которые вызываются через API.

---

### 🔹 FastAPI
FastAPI выступает как управляющий слой:

- принимает запросы
- выбирает pipeline
- запускает обработку
- возвращает результат

---

## 🚀 Возможности

- 📷 Обработка одиночных FITS-кадров
- 🎞 Генерация видео
- 🆚 Разностный анализ (diff)
- 📊 Гистограммы
- 🌡 Тепловые карты
- 🧹 Удаление шумов
- 🎯 Образка по маске
- 🧮 Калибровка изображений
- ⚡ Асинхронная обработка задач

---

## ⚙️ Конфигурация

Создайте `.env` файл:

```env
api_ip = 0.0.0.0
api_port = 8000
api_root = ""

video_tasks_count = 2
img_tasks_count = 3

enable_database_router = True
enable_editor_router = True
enable_edit_router = True
enable_edit_db_router = True

database_ip = 127.0.0.1
database_port = 3306
database_user = root
database_password = ""
database_name = database

log_level = INFO
log_file = app.log
log_to_file = True
log_to_console = True
log_format = %(asctime)s [%(levelname)s] %(name)s: %(message)s
```

---

## ▶️ Запуск

```bash
pip install -r requirements.txt
python main.py
```

Swagger документация:

```
http://localhost:8000/docs
```

---

## 📡 Основные API методы

### 📊 /tasks
Просмотр активных задач

### ❌ /remove/task
Отмена задачи

---

## 🧩 Основные параметры

| Параметр | Описание              |
|----------|-----------------------|
| mask | Маска                 |
| percent_to_trim | Размер маски          |
| dark | Вычитание dark frame  |
| remove_single_pixels | Удаление шумов        |
| correct_matrix | Калибровка            |
| Rayleigh | Физические единицы    |
| type_diff | Тип diff визуализации |
| hists | Гистограммы           |

---

## 🗄 Работа с базой данных

### Проверка

```
GET /database/ping
```

### Кадры

```
GET /database/frames
```

---

## 🛠 Стек

- Python
- FastAPI
- NumPy
- OpenCV
- Matplotlib
- Astropy

---

## 📄 Лицензия

MIT

---

