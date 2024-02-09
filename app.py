from flask import Flask, request, Response, jsonify
from database import db, User
from sqlalchemy import select


app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://v02uazsj0uc9txhv16fu:pscale_pw_3787lvNnmOePNpDb0OH3qJXV1u96Ysrn35uugaVBcxN@aws.connect.psdb.cloud/scd_tool?ssl={'rejectUnauthorized':true}&ssl_ca=cacert.pem"
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/user", methods=['POST'])
def add_user():
    content = request.json
    user = User(**content)
    db.session.add(user)
    db.session.commit()
    return Response("User has been created.", status=201)


@app.route("/user", methods=['GET'])
def get_all_users():
    users = db.session.scalars(select(User))
    return jsonify(list(users))


@app.route("/user/<int:id>", methods=['GET'])
def get_user(user_id):
    user = db.get_or_404(User, user_id)
    return jsonify(user)


@app.route("/user/<int:id>", methods=['PUT'])
def modify_user(user_id):
    content = request.json
    user = db.get_or_404(User, user_id)
    for key in content:
        setattr(user, key, content[key])
    db.session.commit()
    return Response("User has been updated.", status=200)


@app.route("/user/<int:id>", methods=['DELETE'])
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return Response("User has been deleted.", status=200)
