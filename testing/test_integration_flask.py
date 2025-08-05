import sqlalchemy as sa
import pytest
import os 
import auth

from dotenv import load_dotenv

if not load_dotenv(".env.testing"):
    print("ERROR LOADING ENVIRONMENT!")
try: 
    from app import app as flask
except sa.exc.OperationalError:
        pytest.exit(f"Check if Postgres is running. The test expects a Postgres instance to run on port '{port}'.\nThis can be run from Docker with 'docker-compose --profile testing up -d testing_postgres'", returncode=1)

@pytest.fixture
def flask_app():
    yield flask.test_client()


def test_create_user_correct(flask_app):
    response = flask_app.post(f"/register", json={"username": "test-user", "password": "test-password"})
    assert response.status_code == 201

def test_create_user_missing_username(flask_app):
    response = flask_app.post(f"/register", json={"password": "test-password"})
    assert response.status_code == 400

def test_create_user_missing_password(flask_app):
    response = flask_app.post(f"/register", json={"username": "test-user"})
    assert response.status_code == 400

def test_create_user_empty_username(flask_app):
    response = flask_app.post(f"/register", json={"username": "", "password": "test-password"})
    assert response.status_code == 404

def test_create_user_empty_password(flask_app):
    response = flask_app.post(f"/register", json={"username": "test-user", "password": ""})
    assert response.status_code == 404

###########################################

@pytest.fixture
def test_login_correct(flask_app):
    response = flask_app.post(f"/register", json={"username": "test-user", "password": "test-password"})
    assert response.status_code == 201

    response = flask_app.post(f"/login", json={"username": "test-user", "password": "test-password"})
    assert response.status_code == 200
    assert response.json is not None
    assert "access_token" in response.json.keys()
    yield response.json["access_token"]

def test_login_user_not_found(flask_app):
    response = flask_app.post(f"/register", json={"username": "test-user", "password": "test-password"})
    assert response.status_code == 201

    response = flask_app.post(f"/login", json={"username": "not-real-user", "password": "test-password"})
    assert response.status_code == 401

def test_login_incorrect_password(flask_app):
    response = flask_app.post(f"/register", json={"username": "test-user", "password": "test-password"})
    assert response.status_code == 201

    response = flask_app.post(f"/login", json={"username": "test-user", "password": "wrong-password"})
    assert response.status_code == 401

###########################################

def test_get_tasks_correct(flask_app, test_login_correct):
    headers = {"Authorization": f"Bearer {test_login_correct}"}
    response = flask_app.get(f"/tasks", headers=headers)
    assert response.status_code == 200

def test_get_tasks_unathorized(flask_app, test_login_correct):
    invalid_auth_token = auth.gen_jwt({"id": 99999})
    headers = {"Authorization": f"Bearer {invalid_auth_token}"}
    response = flask_app.get(f"/tasks", headers=headers)
    assert response.status_code == 401

###########################################

def test_insert_and_get_task(flask_app, test_login_correct):
    headers = {"Authorization": f"Bearer {test_login_correct}"}
    response = flask_app.post(f"/tasks", json={"title": "Task-title"}, headers=headers)
    assert response.status_code == 200

    response = flask_app.get(f"/tasks", headers=headers)
    assert response.status_code == 200
    assert response.json is not None
    assert response.json[0]["title"] == "Task-title"

def test_insert_task_no_title(flask_app, test_login_correct):
    headers = {"Authorization": f"Bearer {test_login_correct}"}
    response = flask_app.post(f"/tasks", json={"description": "Task-description"}, headers=headers)
    assert response.status_code == 400

###########################################
