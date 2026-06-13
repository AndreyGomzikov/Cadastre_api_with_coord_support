# Служба кадастровых запросов

Сервис принимает кадастровый номер, широту и долготу, отправляет запрос на эмулируемый внешний сервер, получает `true` или `false`, сохраняет запрос и ответ в PostgreSQL и отдаёт историю запросов.

## Стек

- Python 3.9+
- FastAPI, async routes
- PostgreSQL
- asyncpg
- Raw SQL migration
- Docker, Docker Compose
- Pytest

## Что реализовано

- Основной сервис с эндпоинтами `/ping`, `/query`, `/history`, `/result`.
- Отдельный сервис-эмулятор внешнего сервера в папке `external_service`.
- Сохранение кадастрового номера, широты, долготы, ответа внешнего сервиса, HTTP-статуса и даты создания в PostgreSQL.
- История всех запросов и история по конкретному кадастровому номеру.
- Валидация входных данных: кадастровый номер, широта, долгота, `limit`, `offset`.
- Swagger-документация FastAPI: `/docs`.
- Минимальная HTML-админ-панель: `/admin/requests`.
- Тесты функционала через `pytest`.

## Структура

```text
.
├── app/                    # основной сервис
├── external_service/       # отдельный сервис-эмулятор внешнего сервера
├── migrations/             # raw SQL migration
├── tests/                  # pytest
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Запуск через Docker Compose

```bash
docker compose up --build
```

После запуска:

- основной сервис: `http://localhost:8000`
- Swagger UI основного сервиса: `http://localhost:8000/docs`
- минимальная админ-панель: `http://localhost:8000/admin/requests`
- внешний сервис: `http://localhost:8001`
- Swagger UI внешнего сервиса: `http://localhost:8001/docs`

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

### `GET /admin/requests`

Минимальная HTML-админ-панель для просмотра истории запросов.

```bash
open http://localhost:8000/admin/requests
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

Внешний сервис может ждать до 60 секунд. Это настраивается через переменную окружения:

```env
EXTERNAL_MAX_DELAY_SECONDS=60
```

Для соответствия формулировке ТЗ endpoint `/result` также оставлен в основном сервисе на `http://localhost:8000/result`, но сценарий `/query` обращается именно к отдельному внешнему сервису `external_service`.

## Валидация данных

Для запроса `/query` используются ограничения:

- `cadastral_number`: от 5 до 100 символов, только цифры и двоеточия;
- `latitude`: от `-90` до `90`;
- `longitude`: от `-180` до `180`.

Пример некорректного запроса вернёт `422 Unprocessable Entity`.

## Миграции

Используется raw SQL migration:

```text
migrations/001_init.sql
```

При старте приложения миграция применяется автоматически.

## Локальный запуск без Docker

Нужно поднять PostgreSQL и указать `DATABASE_URL`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/cadastral_db"
export EXTERNAL_SERVICE_URL="http://localhost:8001/result"

uvicorn external_service.main:app --host 0.0.0.0 --port 8001
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Для Windows PowerShell переменные можно задать так:

```powershell
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/cadastral_db"
$env:EXTERNAL_SERVICE_URL="http://localhost:8001/result"
```

## Тесты

```bash
pytest
```

Тесты проверяют:

- `/ping`;
- внешний `/result`;
- успешный сценарий `/query` с обращением к внешнему сервису и сохранением результата;
- `/history`;
- фильтр истории по кадастровому номеру;
- `/admin/requests`;
- валидацию корректных и некорректных данных.

## Полезные команды

Остановить и удалить контейнеры:

```bash
docker compose down
```

Остановить и удалить контейнеры вместе с volume PostgreSQL:

```bash
docker compose down -v
```
