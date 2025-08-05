import sqlalchemy as sa
from dotenv import load_dotenv
import os 

import pytest

from InvalidInputException import InvalidInputException
import db

if not load_dotenv(".env.testing"):
    print("ERROR LOADING ENVIRONMENT!")

host = os.environ.get("POSTGRES_HOST")
port = os.environ.get("POSTGRES_PORT")
username = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PASSWORD")
dbname = os.environ.get("POSTGRES_DB")

@pytest.fixture
def empty_db():
    engine, connection = db.create_db_connection(host, port, username, password, dbname)
    yield connection
    connection.close()

@pytest.fixture
def populate_db(empty_db):
    query = db.user_table.insert().values(username="testing_username", password_hash="testing_hashed_password_string")
    empty_db.execute(query)
    tasks = [{"title": "test-task1"}]

    for task in tasks:
        query = db.task_table.insert().values(**task)
        empty_db.execute(query)

def test_get_user_by_username_correct(empty_db, populate_db):
    user = db.get_user_by_username("testing_username", empty_db)
    assert set(user.keys()) == set(["id", "username", "password_hash"])
    assert user["username"] == "testing_username"
    assert user["password_hash"] == "testing_hashed_password_string"

def test_get_user_by_username_incorrect_username(empty_db, populate_db):
    user = db.get_user_by_username("Invalid_testing_username", empty_db)
    assert user is None

def test_get_user_by_username_empty_username(empty_db, populate_db):
    with pytest.raises(InvalidInputException) as exc_info:
        db.get_user_by_username("", empty_db)

    assert "Invalid username: Must be a non-empty string" in str(exc_info.value)

def test_get_user_by_username_invalid_type_username(empty_db, populate_db):
    with pytest.raises(InvalidInputException) as exc_info:
        db.get_user_by_username(1, empty_db)

    assert "Invalid username: Must be a non-empty string" in str(exc_info.value)

########################################################

def test_insert_task_correct(empty_db, populate_db):
    new_task_id = db.insert_task({"title": "Task-Title", "description": "Task-description"}, empty_db)
    query = db.task_table.select().where(db.task_table.c.id == new_task_id)
    task = empty_db.execute(query).fetchone()
    assert task[0] == new_task_id
    assert task[1] is None
    assert task[2] == "Task-Title"
    assert task[3] == "Task-description"
    assert task[4] is None
    assert task[5] is None

def test_insert_task_no_title(empty_db, populate_db):
    with pytest.raises(InvalidInputException) as exc_info:
        db.insert_task({"description": "task-description"}, empty_db)

    assert "title is required for creating a task" in str(exc_info.value)

def test_insert_task_invalid_type_username(empty_db, populate_db):
    with pytest.raises(InvalidInputException) as exc_info:
        db.insert_task("Task Title: this is a task. Description: task-description", empty_db)

    assert "Task must be of type dict" in str(exc_info.value)
