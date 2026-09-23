import pytest
from aiohttp import web
from config import normalize_db_url, Settings
from main import health_check, start_health_server


def test_normalize_db_url():
    # Neon / Render standard postgres URL
    raw_neon = 'postgres://user:secret@ep-cool-123.eu-central-1.aws.neon.tech/neondb?sslmode=require'
    expected = 'postgresql+asyncpg://user:secret@ep-cool-123.eu-central-1.aws.neon.tech/neondb?ssl=require'
    assert normalize_db_url(raw_neon) == expected

    # postgresql:// variant
    raw_pg = 'postgresql://user:secret@ep-cool-123.eu-central-1.aws.neon.tech/neondb?sslmode=require'
    assert normalize_db_url(raw_pg) == expected

    # sqlite should remain unmodified
    sqlite_url = 'sqlite+aiosqlite:///subscriptions.db'
    assert normalize_db_url(sqlite_url) == sqlite_url


def test_settings_validation():
    s = Settings(
        DB_URL='postgres://user:pwd@neon.tech/db?sslmode=require',
        PORT='9000',
    )
    assert s.DB_URL.startswith('postgresql+asyncpg://')
    assert 'ssl=require' in s.DB_URL
    assert s.PORT == 9000


@pytest.mark.asyncio
async def test_health_check_endpoint():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    # Test internal request
    from aiohttp.test_utils import TestClient, TestServer
    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()

    try:
        resp = await client.get('/health')
        assert resp.status == 200
        data = await resp.json()
        assert data['status'] == 'ok'
        assert data['service'] == 'sub_tracker_bot'

        resp_root = await client.get('/')
        assert resp_root.status == 200
    finally:
        await client.close()
        await runner.cleanup()


@pytest.mark.asyncio
async def test_webapp_endpoints():
    from main import serve_index, api_get_subscriptions, cors_middleware
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get('/', serve_index)
    app.router.add_get('/app', serve_index)
    app.router.add_get('/api/subscriptions', api_get_subscriptions)

    from aiohttp.test_utils import TestClient, TestServer
    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()

    try:
        # 1. Test HTML serve
        resp = await client.get('/')
        assert resp.status == 200
        text = await resp.text()
        assert "StopPay" in text

        # 2. Test JSON header on /
        resp_json = await client.get('/', headers={"Accept": "application/json"})
        assert resp_json.status == 200
        data_json = await resp_json.json()
        assert data_json["status"] == "ok"

        # 3. Test subscriptions API
        resp_api = await client.get('/api/subscriptions?currency=RUB')
        assert resp_api.status == 200
        api_data = await resp_api.json()
        assert api_data["status"] == "ok"
        assert len(api_data["subscriptions"]) > 0
        assert "metrics" in api_data
        assert api_data["metrics"]["total_annual"] > 0
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_renew_subscription_api(test_session, monkeypatch):
    import main
    from main import api_renew_subscription, cors_middleware
    from database.requests import get_or_create_user, add_subscription
    from datetime import date
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def mock_session_factory():
        yield test_session

    monkeypatch.setattr(main, 'async_session_factory', mock_session_factory)

    await get_or_create_user(test_session, telegram_id=925951839)
    sub = await add_subscription(
        session=test_session,
        user_id=925951839,
        service_name="TestRenew",
        price=10.0,
        currency="USD",
        period_days=30,
        next_billing_date=date(2026, 10, 1),
    )

    app = web.Application(middlewares=[cors_middleware])
    app.router.add_post('/api/subscriptions/{id}/renew', api_renew_subscription)

    from aiohttp.test_utils import TestClient, TestServer
    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()

    try:
        resp = await client.post(f'/api/subscriptions/{sub.id}/renew')
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "ok"
        assert data["sub_id"] == sub.id
        assert data["next_billing_date"] == "2026-10-31"

        # Not found case
        resp_404 = await client.post('/api/subscriptions/999999/renew')
        assert resp_404.status == 404
    finally:
        await client.close()


