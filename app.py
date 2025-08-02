from flask import Flask, Response, request, redirect, url_for, make_response, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import datetime
import os
import pwd_hashing
from flask_swagger_ui import get_swaggerui_blueprint

if not load_dotenv(".env"):
    print("ERROR LOADING ENVIRONMENT!")

DEBUG = True
from tempRepo import USERS, TASKS

app = Flask(__name__)

CORS(app)
app.secret_key = os.environ.get("FLASK_SECRET")

##################################################
SWAGGER_URL = '/docs'
swagger_config = '/swagger.json' 

@app.route("/swagger.json", methods=["GET"])
def swagger():
    with open('swagger.json') as f:
        return f.read(), 200, {'Content-Type': 'application/json'}

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
    hashed_password = pwd_hashing.hash_password(plaintext_password)

    USERS[username] = hashed_password
    return make_response("User registered", 201)

@app.route("/login", methods=["POST"])
def login(): #! TODO ADD USERS TO SQL
    if ("username" not in request.json or "password" not in request.json):
        return make_response("Bad request", 400)
    
    username, plaintext_password = str(request.json.get("username")), str(request.json.get("password"))
    user_found = username in USERS.keys()

    # IF user is not found use dummy compare to avoid timing attacks
    if (not user_found):
        hashed_password = pwd_hashing.DUMMY_HASH
    else:
        hashed_password = USERS[username]
    
    verify_user = pwd_hashing.check_password_hash(plaintext_password, hashed_password)
    if (not user_found or not verify_user):
        return make_response("Unauthorized", 401) 
    
    return make_response("JWT", 200) #! TODO 

##################################################

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return make_response(jsonify(TASKS), 200)

@app.route("/tasks", methods=["POST"])
def add_task():
    if ("title" not in request.json):
        return make_response("Bad request", 400)
    
    USERS[USERS.keys[0]].append(request.json)
    return make_response("Success", 200)

@app.route("/tasks/<task_id>", methods=["PUT"])
def update_task_by_id(task_id):
    pass

@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task_by_id(task_id):
    pass

##################################################

if __name__ == "__main__":
    # Propagate exceptions for easier debugging
    app.config["PROPAGATE_EXCEPTIONS"] = True

    # Run app on for all hosts (if from docker-compose -> only internal through nginx)
    app.run(host="0.0.0.0",debug = DEBUG)