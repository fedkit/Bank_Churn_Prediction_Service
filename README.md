

# Сервис для предсказания оттока клиентов банка

Этот проект состоит из двух частей:

- **Бэкенд** на **FastAPI** — обрабатывает запросы и выдаёт предсказания.
- **Фронтенд** на **Streamlit** — позволяет загружать данные, визуализировать результаты и анализировать предсказания.

## Быстрый старт

### 1. Локальный запуск (без Docker)

1. **Установка зависимостей:**

```bash
   pip install -r requirements.txt
```

2. Запуск бэкенда:

```bash
uvicorn backend:app --host 0.0.0.0 --port 8000
```

3. Запуск Streamlit-приложения (в отдельном терминале):

```bash
streamlit run streamlit_app.py --server.port 8501
```

4. Проверка:

- FastAPI-документация: [http://localhost:8000/docs](http://localhost:8000/docs)
- Streamlit-интерфейс: [http://localhost:8501](http://localhost:8501)

### 2. Запуск через Docker

1. Сборка и запуск контейнеров:

```bash
docker-compose up --build -d
```

2. Доступ к сервисам:

- Бэкенд: [http://localhost:8000](http://localhost:8000)
- Streamlit: [http://localhost:8501](http://localhost:8501)

2. Остановка:

```bash
docker-compose down
```

## Структура проекта

```bash
bank_churn_prediction_service/
├── backend.py            # Бэкенд (FastAPI)
├── streamlit_app.py      # Фронтенд (Streamlit)
├── Dockerfile.backend    # Dockerfile для бэкенда
├── Dockerfile.streamlit  # Dockerfile для Streamlit
├── docker-compose.yml    # Докер-компоновка сервисов
├── requirements.txt      # Зависимости Python
└── models/              # Папка с сериализованными моделями (*.pkl)
```

## Основные эндпоинты FastAPI

- **POST `/predict_batch`**  
    Принимает пакет данных клиентов и возвращает для каждого клиента:
    
    - `prediction` (0 — останется, 1 — уйдёт)
    - `churn_probability` (вероятность оттока).
    
- **GET `/feature_importances`**  
    Принимает параметр `country` (France, Spain, Germany) и возвращает важность признаков для выбранной страны.
