import pytest


@pytest.mark.asyncio
async def test_healthcheck_should_return_ok(client):

    response = await client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
