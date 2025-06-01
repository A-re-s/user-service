import pytest


@pytest.mark.asyncio
async def test_create_project(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "user1", "password": "pass"}
    )
    token_response = await async_client.post(
        "/api/v1/token", json={"login": "user1", "password": "pass"}
    )
    access_token = token_response.json()["access_token"]

    response = await async_client.post(
        "/api/v1/projects/",
        json={"name": "Project Alpha"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Project Alpha"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_projects(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "user2", "password": "pass"}
    )
    token_response = await async_client.post(
        "/api/v1/token", json={"login": "user2", "password": "pass"}
    )
    access_token = token_response.json()["access_token"]

    await async_client.post(
        "/api/v1/projects/",
        json={"name": "Project Beta"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    response = await async_client.get(
        "/api/v1/projects/", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(project["name"] == "Project Beta" for project in data)


@pytest.mark.asyncio
async def test_get_project(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "user3", "password": "pass"}
    )
    token_response = await async_client.post(
        "/api/v1/token", json={"login": "user3", "password": "pass"}
    )
    access_token = token_response.json()["access_token"]

    create_response = await async_client.post(
        "/api/v1/projects/",
        json={"name": "Project Gamma"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    project_id = create_response.json()["id"]

    response = await async_client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Project Gamma"


@pytest.mark.asyncio
async def test_update_project(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "user4", "password": "pass"}
    )
    token_response = await async_client.post(
        "/api/v1/token", json={"login": "user4", "password": "pass"}
    )
    access_token = token_response.json()["access_token"]

    create_response = await async_client.post(
        "/api/v1/projects/",
        json={"name": "Project Delta"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    project_id = create_response.json()["id"]

    response = await async_client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Project Delta Updated"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Project Delta Updated"


@pytest.mark.asyncio
async def test_delete_project(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "user5", "password": "pass"}
    )
    token_response = await async_client.post(
        "/api/v1/token", json={"login": "user5", "password": "pass"}
    )
    access_token = token_response.json()["access_token"]

    create_response = await async_client.post(
        "/api/v1/projects/",
        json={"name": "Project Epsilon"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    project_id = create_response.json()["id"]

    response = await async_client.delete(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204

    get_response = await async_client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert get_response.status_code == 404
