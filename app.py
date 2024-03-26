from flask import Flask
from database import db
from routes.user import user_routes
from routes.session import session_routes, login_manager
from routes.physician import physician_routes
from routes.match import match_routes
from routes.insurance import insurance_routes
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["APP_SECRET_KEY"]

# database
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://v02uazsj0uc9txhv16fu:pscale_pw_3787lvNnmOePNpDb0OH3qJXV1u96Ysrn35uugaVBcxN@aws.connect.psdb.cloud/scd_tool?ssl={'rejectUnauthorized':true}&ssl_ca=cacert.pem"
db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

# routes
app.register_blueprint(user_routes)
app.register_blueprint(session_routes)
app.register_blueprint(physician_routes)
app.register_blueprint(match_routes)
app.register_blueprint(insurance_routes)

if __name__ == "__main__":
    app.run(debug=True)
