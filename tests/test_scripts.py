import pytest


@pytest.mark.asyncio
async def test_create_script(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "user6", "password": "pass"}
    )
    token_response = await async_client.post(
        "/api/v1/token", json={"login": "user6", "password": "pass"}
    )
    access_token = token_response.json()["access_token"]

    project_response = await async_client.post(
        "/api/v1/projects/",
        json={"name": "Project Zeta"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    project_id = project_response.json()["id"]

    response = await async_client.post(
        f"/api/v1/projects/{project_id}/scripts",
        json={"path": "script.py", "source_code": "print('Hello World')"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["path"] == "script.py"
    assert data["source_code"] == "print('Hello World')"


@pytest.mark.asyncio
async def test_get_scripts(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "user7", "password": "pass"}
    )
    token_response = await async_client.post(
        "/api/v1/token", json={"login": "user7", "password": "pass"}
    )
    access_token = token_response.json()["access_token"]

    project_response = await async_client.post(
        "/api/v1/projects/",
        json={"name": "Project Eta"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    project_id = project_response.json()["id"]

    await async_client.post(
        f"/api/v1/projects/{project_id}/scripts",
        json={"path": "script1.py", "source_code": "print('Script 1')"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    response = await async_client.get(
        f"/api/v1/projects/{project_id}/scripts",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(script["path"] == "script1.py" for script in data)


@pytest.mark.asyncio
async def test_get_script(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "user8", "password": "pass"}
    )
    token_response = await async_client.post(
        "/api/v1/token", json={"login": "user8", "password": "pass"}
    )
    access_token = token_response.json()["access_token"]

    project_response = await async_client.post(
        "/api/v1/projects/",
        json={"name": "Project Theta"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    project_id = project_response.json()["id"]

    script_response = await async_client.post(
        f"/api/v1/projects/{project_id}/scripts",
        json={"path": "script2.py", "source_code": "print('Script 2')"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    script_id = script_response.json()["id"]

    response = await async_client.get(
        f"/api/v1/projects/{project_id}/scripts/{script_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == script_id
    assert data["path"] == "script2.py"


@pytest.mark.asyncio
async def test_update_script(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "testuser", "password": "testpass"}
    )
    login_response = await async_client.post(
        "/api/v1/token", json={"login": "testuser", "password": "testpass"}
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    project_response = await async_client.post(
        "/api/v1/projects/", json={"name": "Test Project"}, headers=headers
    )
    project_id = project_response.json()["id"]

    script_data = {"path": "script.py", "source_code": "print('Hello, World!')"}
    script_response = await async_client.post(
        f"/api/v1/projects/{project_id}/scripts", json=script_data, headers=headers
    )
    script_id = script_response.json()["id"]

    updated_data = {"path": "updated_script.py", "source_code": "print('Updated!')"}
    update_response = await async_client.put(
        f"/api/v1/projects/{project_id}/scripts/{script_id}",
        json=updated_data,
        headers=headers,
    )
    assert update_response.status_code == 200
    updated_script = update_response.json()
    assert updated_script["path"] == "updated_script.py"
    assert updated_script["source_code"] == "print('Updated!')"


@pytest.mark.asyncio
async def test_delete_script(async_client):
    await async_client.post(
        "/api/v1/register", json={"login": "testuser", "password": "testpass"}
    )
    login_response = await async_client.post(
        "/api/v1/token", json={"login": "testuser", "password": "testpass"}
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    project_response = await async_client.post(
        "/api/v1/projects/", json={"name": "Test Project"}, headers=headers
    )
    project_id = project_response.json()["id"]

    script_data = {"path": "script.py", "source_code": "print('Hello, World!')"}
    script_response = await async_client.post(
        f"/api/v1/projects/{project_id}/scripts", json=script_data, headers=headers
    )
    script_id = script_response.json()["id"]

    delete_response = await async_client.delete(
        f"/api/v1/projects/{project_id}/scripts/{script_id}", headers=headers
    )
    assert delete_response.status_code == 204

    get_response = await async_client.get(
        f"/api/v1/projects/{project_id}/scripts/{script_id}", headers=headers
    )
    assert get_response.status_code == 404
