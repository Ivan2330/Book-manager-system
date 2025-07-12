import pytest

@pytest.mark.asyncio
async def test_get_all_books(client):
    response = await client.get("/books/all")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_books_with_pagination(client):
    response = await client.get("/books/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 2

@pytest.mark.asyncio
async def test_export_books_json(client):
    response = await client.get("/books/export?format=json")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


