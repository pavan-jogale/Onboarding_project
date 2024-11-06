import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from fastapi_tasks.main import app
from fastapi_tasks.database import engine, Base

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

def test_index(client):
    response = client.get("/")
    assert response.json()["message"] == "Welcome to the Task Manager API"

def test_signup(client):
    response = client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_signup_integrity_error(client):
    client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_login(client):
    client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200

def test_invalid_login(client):
    client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/login", json={"username": "testuser1", "password": "testpass"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

def test_create_task(client):
    client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    user_id = response.json()["user_id"]
    task_response = client.post("/tasks/?user_id=" + str(user_id), json={"title": "Test Task", "due_date": "2024-12-31T00:00:00Z"}, headers={"Authorization": f"Bearer {user_id}"})

    assert task_response.status_code == 200
    assert task_response.json()["title"] == "Test Task"

def test_get_all_tasks(client):
    client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    user_id = response.json()["user_id"]
    for i in range(0,10):
        title_name = "Test Task"+str(i)
        client.post("/tasks/?user_id=" + str(user_id), json={"title": title_name, "due_date": "2024-12-31T00:00:00Z"}, headers={"Authorization": f"Bearer {user_id}"})
    task_get_response = client.get("/tasks/?user_id=" + str(user_id), headers={"Authorization": f"Bearer {user_id}"})
    print(task_get_response.json())
    assert task_get_response.status_code == 200
    assert len(task_get_response.json()) >= 2

# @pytest.mark.asyncio
# async def test_async_read_tasks():
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         await client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
#         response = await client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
#         user_id = response.json()["user_id"]
#         response = await client.get(f"/tasks/?user_id={user_id}")
#         assert response.status_code == 200
#         assert isinstance(response.json(), list)

def test_update_task(client):
    client.post("/auth/signup/", json={"username": "testuser2", "password": "testpass2"})
    response = client.post("/auth/login/", json={"username": "testuser2", "password": "testpass2"})
    user_id = response.json()["user_id"]
    task_create_response = client.post("/tasks/?user_id=" + str(user_id), json={"title": "Test Task 2", "due_date": "2024-10-31T00:00:00Z"}, headers={"Authorization": f"Bearer {user_id}"})
    task_id = task_create_response.json()["id"]
    task_update_response = client.put("/tasks/"+str(task_id)+"/?user_id=" + str(user_id), json={"title": "Test Task 22", "due_date": "2024-11-30T00:00:00Z"}, headers={"Authorization": f"Bearer {user_id}"})

    assert task_update_response.status_code == 200
    assert task_update_response.json()["title"] == "Test Task 22"

def test_invalid_update_task(client):
    client.post("/auth/signup/", json={"username": "testuser2", "password": "testpass2"})
    response = client.post("/auth/login/", json={"username": "testuser2", "password": "testpass2"})
    user_id = response.json()["user_id"]
    task_create_response = client.post("/tasks/?user_id=" + str(user_id), json={"title": "Test Task 2", "due_date": "2024-10-31T00:00:00Z"}, headers={"Authorization": f"Bearer {user_id}"})
    task_id = task_create_response.json()["id"]
    task_update_response = client.put("/tasks/"+str(task_id+1)+"/?user_id=" + str(user_id), json={"title": "Test Task 22", "due_date": "2024-11-30T00:00:00Z"}, headers={"Authorization": f"Bearer {user_id}"})

    assert task_update_response.status_code == 404
    assert task_update_response.json()["detail"] == "Task not found"

def test_delete_task(client):
    client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    user_id = response.json()["user_id"]
    client.post("/tasks/?user_id=" + str(user_id), json={"title": "Test Task", "due_date": "2024-12-31T00:00:00Z"}, headers={"Authorization": f"Bearer {user_id}"})
    created_task = client.post("/tasks/?user_id=" + str(user_id), json={"title": "Test Task 2", "due_date": "2024-11-30T00:00:00Z"}, headers={"Authorization": f"Bearer {user_id}"})
    task_id_to_detele = created_task.json()["id"]
    task_get_response = client.get("/tasks/?user_id=" + str(user_id), headers={"Authorization": f"Bearer {user_id}"})
    total_tasks = len(task_get_response.json())
    task_delete_response = client.delete("/tasks/"+str(task_id_to_detele)+"/?user_id=" + str(user_id), headers={"Authorization": f"Bearer {user_id}"})
    assert task_delete_response.status_code == 200
    assert task_delete_response.json()["detail"] == "Task deleted"
    task_get_response = client.get("/tasks/?user_id=" + str(user_id), headers={"Authorization": f"Bearer {user_id}"})
    assert len(task_get_response.json()) == total_tasks-1

def test_invalid_delete_task(client):
    client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    user_id = response.json()["user_id"]
    client.post("/tasks/?user_id=" + str(user_id), json={"title": "Test Task", "due_date": "2024-12-31T00:00:00Z"}, headers={"Authorization": f"Bearer {user_id}"})
    created_task = client.post("/tasks/?user_id=" + str(user_id), json={"title": "Test Task 2", "due_date": "2024-11-30T00:00:00Z"}, headers={"Authorization": f"Bearer {user_id}"})
    task_id_to_detele = created_task.json()["id"]
    task_delete_response = client.delete("/tasks/"+str(task_id_to_detele+1)+"/?user_id=" + str(user_id), headers={"Authorization": f"Bearer {user_id}"})
    assert task_delete_response.status_code == 404
    assert task_delete_response.json()["detail"] == "Task not found"