from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from dbdash.config import Config
from cryptography.fernet import Fernet
import base64

mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

def DecryptValue(inputValue):
    key = Config.SECRET_KEY.encode()
    print(key)
    fernet = Fernet(base64.urlsafe_b64encode(key))
    print(fernet)
    return fernet.decrypt(inputValue).decode()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    from dbdash.main.routes import main
    from dbdash.users.routes import users
    from dbdash.dbs.routes import dbs
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(dbs)
    app.jinja_env.globals.update(DecryptValue=DecryptValue)
    return app



