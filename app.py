from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

db = SQLAlchemy()
app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://SCDTool_greaterjar:c726acbc8f94cfd93d6656c4a2fb64e4791871f1@nks.h.filess.io:3307/SCDTool_greaterjar"
app.config[
    "SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://v02uazsj0uc9txhv16fu:pscale_pw_3787lvNnmOePNpDb0OH3qJXV1u96Ysrn35uugaVBcxN@aws.connect.psdb.cloud/scd_tool?ssl={'rejectUnauthorized':true}&ssl_ca=cacert.pem"
db.init_app(app)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(30))


@app.route("/user", methods=['POST'])
def add_user():
    content = request.json
    user = User(
        username=content["username"],
        email=content["email"],
    )
    db.session.add(user)
    db.session.commit()
    return Response("User has been created.", status=201)


# @app.route("/user/<id>", methods=['GET'])
# def get_user(id):
#     user = db.get_or_404(entity=User, ident=id)
#     return Response(user, status=200)


# @app.route("/user/<id>", methods=['DELETE'])
# def get_user():
#     content = request.json
#     user = User(
#         username=content["username"],
#         email=content["email"],
#     )
#     db.session.add(user)
#     db.session.commit()
#     Response("{'a','b'}", status=201)
