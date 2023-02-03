from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
app = Flask(__name__)
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth_bp.login'
login_manager.login_message = "You need to be Login!"

def init_app():
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        from .auth import auth_bp
        from .routes import views
        from .handlers import errors
        from .models import User

        app.register_blueprint(auth_bp)
        app.register_blueprint(views)
        app.register_blueprint(errors)

        db.create_all()

        login_manager.init_app(app)
        mail.init_app(app)

        @login_manager.user_loader
        def load_user(id):
            return User.query.get(int(id))

        return app