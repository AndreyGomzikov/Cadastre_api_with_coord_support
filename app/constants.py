API_TITLE = "Cadastral Query Service"
API_DESCRIPTION = (
    "Сервис принимает кадастровый номер, широту и долготу, "
    "обращается к эмулируемому внешнему серверу, сохраняет запрос "
    "и результат в PostgreSQL."
)
API_VERSION = "1.1.0"

PING_STATUS_KEY = "status"
PING_STATUS_OK = "ok"

CADASTRAL_NUMBER_PATTERN = r"^[0-9:]+$"
CADASTRAL_NUMBER_MIN_LENGTH = 5
CADASTRAL_NUMBER_MAX_LENGTH = 100
CADASTRAL_NUMBER_EXAMPLE = "77:01:0004010:1234"
CADASTRAL_NUMBER_DESCRIPTION = (
    "Кадастровый номер. Допускаются цифры и двоеточия."
)


MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180
LATITUDE_EXAMPLE = 55.7558
LONGITUDE_EXAMPLE = 37.6173

DEFAULT_HISTORY_LIMIT = 100
MAX_HISTORY_LIMIT = 500
DEFAULT_HISTORY_OFFSET = 0
MIN_HISTORY_LIMIT = 1
MIN_HISTORY_OFFSET = 0

DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@db:5432/cadastral_db"
DEFAULT_EXTERNAL_SERVICE_URL = "http://external:8001/result"
DEFAULT_EXTERNAL_TIMEOUT_SECONDS = 65.0

ADMIN_PAGE_TITLE = "Cadastral requests admin"
ADMIN_HEADER = "История кадастровых запросов"
ADMIN_DESCRIPTION = (
    "Минимальная админ‑панель для просмотра сохранённых запросов."
)
