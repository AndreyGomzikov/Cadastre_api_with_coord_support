# Служба кадастровых запросов

## Описание
Сервис, который принимает кадастровый номер, широту и долготу, отправляет запрос на эмулируемый внешний сервер, получает "true" или "false", сохраняет запрос и ответ в PostgreSQL и отдаёт историю запросов.
В проекте реализовано:
- Основной сервис с эндпоинтами "/ping", "/query", "/history", "/result".
- Отдельный сервис-эмулятор внешнего сервера в папке "external_service".
- Сохранение кадастрового номера, широты, долготы, ответа внешнего сервиса, HTTP-статуса и даты создания в PostgreSQL.
- История всех запросов и история по конкретному кадастровому номеру.
- Валидация входных данных: кадастровый номер, широта, долгота, "cadastral_number", "limit`, "offset".
- Swagger-документация FastAPI: "/docs".
- Минимальная HTML-админ-панель: "/admin/requests".
- Тесты функционала через "pytest".

## Стек
- Python 3.9+
- FastAPI, async routes
- PostgreSQL
- asyncpg
- Raw SQL migration
- Docker, Docker Compose
- Pytest


## Файл .env
В проект добавлен готовый .env для запуска через Docker Compose:

```env
POSTGRES_DB=cadastral_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@db:5432/cadastral_db
EXTERNAL_SERVICE_URL=http://external:8001/result
EXTERNAL_TIMEOUT_SECONDS=65
EXTERNAL_MAX_DELAY_SECONDS=60
```


## Запуск через Docker Compose
```bash
docker compose build --no-cache
docker compose build up
```


После запуска:
- основной сервис:
http://localhost:8000
- Swagger UI основного сервиса:
http://localhost:8000/docs
- минимальная админ-панель:
http://localhost:8000/admin/requests
- внешний сервис:
http://localhost:8001
- Swagger UI внешнего сервиса:
http://localhost:8001/docs

## Эндпоинты

### `GET /ping`
Проверка, что основной сервер запустился.
```bash
curl http://localhost:8000/ping
```

Ответ:
```json
{"status":"ok"}
```

### `POST /query`
Принимает кадастровый номер, широту и долготу. Основной сервис отправляет запрос во внешний сервис `/result`, ждёт ответ и сохраняет запрос + ответ в БД.

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "cadastral_number": "77:01:0004010:1234",
    "latitude": 55.7558,
    "longitude": 37.6173
  }'
```

Пример ответа:
```json
{
  "id": 1,
  "cadastral_number": "77:01:0004010:1234",
  "latitude": 55.7558,
  "longitude": 37.6173,
  "result": true,
  "created_at": "2026-06-13T10:00:00.000000Z"
}
```

### `GET /history`
Получение всей истории запросов.

```bash
curl "http://localhost:8000/history"
```

Поддерживаются параметры:
- `cadastral_number` — фильтр по кадастровому номеру;
- `limit` — лимит записей, от 1 до 500;
- `offset` — смещение.

Пример истории по кадастровому номеру:
```bash
curl "http://localhost:8000/history?cadastral_number=77:01:0004010:1234&limit=10&offset=0"
```

Также поддерживаются параметры:
- `cadastral_number`;
- `limit`;
- `offset`.

Пример:
```bash
curl "http://localhost:8000/admin/requests?cadastral_number=77:01:0004010:1234"
```

### `POST /result`
Эндпоинт эмулируемого внешнего сервера. Основной рабочий вариант находится в отдельном сервисе на порту `8001`.

```bash
curl -X POST http://localhost:8001/result \
  -H "Content-Type: application/json" \
  -d '{
    "cadastral_number": "77:01:0004010:1234",
    "latitude": 55.7558,
    "longitude": 37.6173
  }'
```

Ответ:
```json
{"result":true}
```

## Валидация данных
Для запроса /query используются ограничения:
- cadastral_number: от 5 до 100 символов, только цифры и двоеточия;
- latitude: от -90 до 90;
- longitude: от -180 до 180.


## Тесты
```bash
pytest
```
Тесты проверяют:
- /ping;
- внешний /result;
- успешный сценарий /query с обращением к внешнему сервису и сохранением результата;
- /history;
- фильтр истории по кадастровому номеру;
- /admin/requests;
- валидацию корректных и некорректных данных.


# Тестовое задание выполнил
[Андрей Гомзиков](https://github.com/AndreyGomzikov)

