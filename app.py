from flask import Flask, Response, request, redirect, url_for, make_response, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import datetime
import os
import jwt
import auth
from flask_swagger_ui import get_swaggerui_blueprint

from InvalidInputException import InvalidInputException

if not load_dotenv(".env"):
    print("ERROR LOADING ENVIRONMENT!")

DEBUG = True
HOST = os.environ.get("FLASK_HOST")
PORT = os.environ.get("FLASK_PORT")

import db

app = Flask(__name__)

CORS(app)
app.secret_key = os.environ.get("FLASK_SECRET")
db.jwt_secret_key = app.secret_key

##################################################
SWAGGER_URL = '/docs'
swagger_config = '/swagger.json' 

@app.route("/swagger.json", methods=["GET"])
def swagger():
    return make_response(render_template("swagger.json", **{"HOST": HOST, "PORT": PORT}), 200)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    swagger_config,
    config={
        'app_name': "Flask Swagger Example"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

##################################################

@app.route("/register", methods=["POST"])
def register():
    if ("username" not in request.json or "password" not in request.json):
        return make_response("Bad request", 400)
    username, plaintext_password = str(request.json.get("username")), str(request.json.get("password"))

    try:
        hashed_password = auth.hash_password(plaintext_password).decode()
        db.insert_user(username,hashed_password)
    except InvalidInputException as e:
        return make_response(str(e), 404)

    return make_response({"username": username, "password": plaintext_password}, 201)

@app.route("/login", methods=["POST"])
def login(): #! TODO ADD USERS TO SQL
    if ("username" not in request.json or "password" not in request.json):
        return make_response("Bad request", 400)
    
    username, plaintext_password = str(request.json.get("username")), str(request.json.get("password"))

    try:
        user = db.get_user_by_username(username)
    except InvalidInputException as e:
        return make_response(str(e), 404)

    user_found = user is not None

    # IF user is not found use dummy compare to avoid timing attacks
    if (not user_found):
        hashed_password = auth.DUMMY_HASH
    else:
        hashed_password = user["password_hash"]
    
    try:
        user_password_verified = auth.check_password_hash(plaintext_password, hashed_password)
    except InvalidInputException as e:
        return make_response(str(e), 404)

    if (not user_found or not user_password_verified):
        return make_response("Unauthorized", 401) 
    
    token = auth.gen_jwt(user)

    return make_response({"access_token": token}, 200) #! TODO 

##################################################

@app.route("/tasks", methods=["GET"])
@auth.JWT_required
def get_tasks(user_id):

    try:
        task_list = db.get_task_list_by_user_id(user_id)
    except InvalidInputException as e:
        return make_response(str(e), 404)

    return make_response(jsonify(task_list), 200)
    return make_response(jsonify(TASKS), 200)

@app.route("/tasks", methods=["POST"])
@auth.JWT_required
def add_task(user_id):
    if ("title" not in request.json):
        return make_response("Bad request", 400)

    task = request.json
    task["user_id"] = user_id

    try:
        db.insert_task(task)
    except InvalidInputException as e:
        return make_response(str(e), 404)

    
    return make_response(task, 200)

@app.route("/tasks/<int:task_id>", methods=["PUT"])
@auth.JWT_required
def update_task_by_id(task_id, user_id):
    task = request.json
    task["id"] = task_id

    try:
        db.update_task(task, user_id)
    except InvalidInputException as e:
        return make_response(str(e), 404)

    return make_response("Success", 200)

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@auth.JWT_required
def delete_task_by_id(task_id, user_id):
    try:
        db.delete_task_by_id(task_id, user_id)
    except InvalidInputException as e:
        return make_response(str(e), 404)

    return make_response("Success", 200)

##################################################

if __name__ == "__main__":
    # Propagate exceptions for easier debugging
    app.config["PROPAGATE_EXCEPTIONS"] = True

    # Run app on for all hosts (if from docker-compose -> only internal through nginx)
    app.run(host=HOST, port=PORT, debug=DEBUG)
