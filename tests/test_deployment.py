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
