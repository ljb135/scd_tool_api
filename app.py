from flask import Flask
from database import db
from routes.user import user_routes


app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://v02uazsj0uc9txhv16fu:pscale_pw_3787lvNnmOePNpDb0OH3qJXV1u96Ysrn35uugaVBcxN@aws.connect.psdb.cloud/scd_tool?ssl={'rejectUnauthorized':true}&ssl_ca=cacert.pem"
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(user_routes)
