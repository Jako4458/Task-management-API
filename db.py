import os
from dotenv import load_dotenv
import sqlalchemy as sa

from InvalidInputException import InvalidInputException

metadata = sa.MetaData()

user_table = sa.Table("User",
                     metadata,
                     sa.Column("id", sa.Integer, primary_key=True),
                      sa.Column("username", sa.String), #! TODO MAKE UNIQUE  
                     sa.Column("password_hash", sa.String),
                     )

task_table = sa.Table("Task",
                     metadata,
                     sa.Column("id", sa.Integer, primary_key=True),
                     sa.Column("user_id", sa.Integer, sa.ForeignKey("User.id")),
                     sa.Column("title", sa.String),
                     sa.Column("description", sa.String),
                     sa.Column("due_date", sa.DateTime),
                     sa.Column("is_completed", sa.Boolean),
                     )

def create_db_connection(host, port, username, password, dbname):

    connection_string = f"postgresql://{username}:{password}@{host}/{dbname}"

    engine = sa.create_engine(connection_string)
    connection = engine.connect()

    metadata.drop_all(engine)

    metadata.create_all(engine)

    return engine, connection

##################################################

def insert_user(username, hashed_password_string, connection):
    if not isinstance(username, str) or username.strip() == "": raise InvalidInputException("Invalid username: Must be a non-empty string")
    if not isinstance(hashed_password_string, str) or hashed_password_string.strip() == "": raise InvalidInputException("Invalid hashed_password_string: Must be a non-empty string")

    query = user_table.insert().values(username=username, password_hash=hashed_password_string).returning(user_table.c.id)
    new_user_id = connection.execute(query)
    return new_user_id.fetchone()[0]
    
def get_user_by_username(username, connection):
    if not isinstance(username, str) or username.strip() == "": raise InvalidInputException("Invalid username: Must be a non-empty string")

    query = user_table.select().where(user_table.c.username == username)
    user = connection.execute(query).fetchone()

    if user is None: return None
    
    return {"id": user[0], "username": user[1], "password_hash": user[2]}

def get_user_by_id(user_id, connection):
    if not isinstance(user_id, int): raise InvalidInputException("Invalid user_id: Must be int")

    query = user_table.select().where(user_table.c.id == user_id)
    user = connection.execute(query).fetchone()

    if user is None: return None
    
    return {"id": user[0], "username": user[1], "password_hash": user[2]}

def insert_task(task, connection):
    if not isinstance(task, dict): raise InvalidInputException("Task must be of type dict")
    if "title" not in task.keys(): raise InvalidInputException("title is required for creating a task")

    query = task_table.insert().values(**task).returning(task_table.c.id)
    new_task_id = connection.execute(query)
    return new_task_id.fetchone()[0]

def get_task_by_id(task_id, connection):
    if not isinstance(task_id, int): raise InvalidInputException("Invalid task_id: Must be int")

    query = task_table.select().where(task_table.c.id == task_id)
    task = connection.execute(query).fetchone()

    if task is None: return None
    
    return {"id": task[0], "user_id": task[1], "title": task[2], "description": task[3], "due_date": task[4], "is_completed": task[5]}


def get_task_list_by_user_id(user_id, connection):
    if not isinstance(user_id, int): raise InvalidInputException("Invalid user_id: Must be int")

    query = task_table.select().where(task_table.c.user_id == user_id)
    task_list = connection.execute(query)

    if task_list is None: return []
    
    return_list = []
    for task in task_list:
        return_list.append({"id": task[0], "user_id": task[1], "title": task[2], "description": task[3], "due_date": task[4], "is_completed": task[5]})

    return return_list

def update_task(task, user_id, connection):
    if "id" not in task.keys() or not isinstance(task["id"], int): raise InvalidInputException("Missing or Invalid task_id: Must be int")

    query = sa.update(task_table).where(task_table.c.user_id == user_id).where(task_table.c.id == task["id"]).values(**task)
    result = connection.execute(query)
    if result.rowcount == 0: raise InvalidInputException("Invalid task_id: task_id not found")

def delete_task_by_id(task_id, user_id, connection):
    if not isinstance(task_id, int): raise InvalidInputException("Invalid task_id: Must be int")

    query = task_table.delete().where(task_table.c.user_id == user_id).where(task_table.c.id == task_id)
    result = connection.execute(query)
    if result.rowcount == 0: raise InvalidInputException("Invalid task_id: task_id not found")

##################################################

if __name__ == "__main__":
    if not load_dotenv(".env"):
        print("ERROR LOADING ENVIRONMENT!")

    host = os.environ.get("POSTGRES_HOST")
    port = os.environ.get("POSTGRES_PORT")
    username = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    dbname = os.environ.get("POSTGRES_DB")

    engine, connection = create_db_connection(host, port, username, password, dbname)
    print(get_user_by_username("string", connection))
