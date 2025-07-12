# app/tests/test_authors.py

import pytest

@pytest.mark.asyncio
async def test_get_authors(client):
    response = await client.get("/authors/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
