from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.main import app as main_app
from app.schemas import QueryRequest
from external_service.main import app as external_app


SAMPLE_PAYLOAD = {
    "cadastral_number": "77:01:0004010:1234",
    "latitude": 55.7558,
    "longitude": 37.6173,
}

SAMPLE_ROW = {
    "id": 1,
    "cadastral_number": "77:01:0004010:1234",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "external_result": True,
    "external_status_code": 200,
    "created_at": datetime(2026, 6, 13, 10, 0, tzinfo=timezone.utc),
}


@pytest.mark.asyncio
async def test_ping() -> None:
    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/ping")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_external_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXTERNAL_MAX_DELAY_SECONDS", "0")
    transport = ASGITransport(app=external_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/result", json=SAMPLE_PAYLOAD)

    assert response.status_code == 200
    assert isinstance(response.json()["result"], bool)


@pytest.mark.asyncio
async def test_query_calls_external_service_and_saves_to_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saved_args: Dict[str, Any] = {}

    class FakeExternalResponse:
        status_code = 200

        def json(self) -> Dict[str, bool]:
            return {"result": True}

        def raise_for_status(self) -> None:
            return None

    class FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, *args: Any) -> None:
            return None

        async def post(self, url: str, json: Dict[str, Any]) -> FakeExternalResponse:
            saved_args["external_url"] = url
            saved_args["external_payload"] = json
            return FakeExternalResponse()

    async def fake_save_request_result(
        pool: object,
        payload: QueryRequest,
        result: bool,
        status_code: int,
    ) -> Dict[str, Any]:
        saved_args["pool"] = pool
        saved_args["payload"] = payload
        saved_args["result"] = result
        saved_args["status_code"] = status_code
        return SAMPLE_ROW

    main_app.state.pool = object()
    monkeypatch.setattr("app.main.httpx.AsyncClient", FakeAsyncClient)
    monkeypatch.setattr("app.main.save_request_result", fake_save_request_result)

    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/query", json=SAMPLE_PAYLOAD)

    assert response.status_code == 201
    assert response.json()["result"] is True
    assert saved_args["external_payload"] == SAMPLE_PAYLOAD
    assert saved_args["payload"].cadastral_number == SAMPLE_PAYLOAD["cadastral_number"]
    assert saved_args["result"] is True
    assert saved_args["status_code"] == 200


@pytest.mark.asyncio
async def test_history_returns_all_records(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_get_history(
        pool: object,
        cadastral_number: Optional[str],
        limit: int,
        offset: int,
    ) -> List[Dict[str, Any]]:
        assert cadastral_number is None
        assert limit == 100
        assert offset == 0
        return [SAMPLE_ROW]

    main_app.state.pool = object()
    monkeypatch.setattr("app.main.get_history", fake_get_history)

    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/history")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["cadastral_number"] == SAMPLE_PAYLOAD["cadastral_number"]
    assert data[0]["external_status_code"] == 200


@pytest.mark.asyncio
async def test_history_can_filter_by_cadastral_number(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: Dict[str, Any] = {}

    async def fake_get_history(
        pool: object,
        cadastral_number: Optional[str],
        limit: int,
        offset: int,
    ) -> List[Dict[str, Any]]:
        captured["cadastral_number"] = cadastral_number
        captured["limit"] = limit
        captured["offset"] = offset
        return [SAMPLE_ROW]

    main_app.state.pool = object()
    monkeypatch.setattr("app.main.get_history", fake_get_history)

    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/history?cadastral_number=77:01:0004010:1234&limit=10&offset=0"
        )

    assert response.status_code == 200
    assert captured["cadastral_number"] == SAMPLE_PAYLOAD["cadastral_number"]
    assert captured["limit"] == 10
    assert captured["offset"] == 0


@pytest.mark.asyncio
async def test_admin_requests_returns_html(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_get_history(
        pool: object,
        cadastral_number: Optional[str],
        limit: int,
        offset: int,
    ) -> List[Dict[str, Any]]:
        return [SAMPLE_ROW]

    main_app.state.pool = object()
    monkeypatch.setattr("app.main.get_history", fake_get_history)

    transport = ASGITransport(app=main_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/admin/requests")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "77:01:0004010:1234" in response.text


def test_query_request_validation_accepts_correct_data() -> None:
    payload = QueryRequest(**SAMPLE_PAYLOAD)

    assert payload.cadastral_number == "77:01:0004010:1234"


@pytest.mark.parametrize(
    "payload",
    [
        {"cadastral_number": "abc", "latitude": 55.7558, "longitude": 37.6173},
        {"cadastral_number": "77:01:0004010:1234", "latitude": 100, "longitude": 37.6173},
        {"cadastral_number": "77:01:0004010:1234", "latitude": 55.7558, "longitude": 200},
    ],
)
def test_query_request_validation_rejects_invalid_data(
    payload: Dict[str, Any],
) -> None:
    with pytest.raises(ValidationError):
        QueryRequest(**payload)
