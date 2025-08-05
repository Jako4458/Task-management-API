import pytest
import os 
import auth

from app import app as flask

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
    response = flask_app.post(f"/login", json={"username": "test-user", "password": "test-password"})
    assert response.status_code == 200
    assert response.json is not None
    assert "access_token" in response.json.keys()
    yield response.json["access_token"]

def test_login_user_not_found(flask_app):
    response = flask_app.post(f"/register", json={"username": "test-user", "password": "test-password"})
    response = flask_app.post(f"/login", json={"username": "not-real-user", "password": "test-password"})
    assert response.status_code == 401

def test_login_incorrect_password(flask_app):
    response = flask_app.post(f"/register", json={"username": "test-user", "password": "test-password"})
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
