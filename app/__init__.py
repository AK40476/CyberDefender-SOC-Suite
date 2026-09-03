from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dev-secret-key-change-later"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cyberdefender.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes.auth import auth
    app.register_blueprint(auth)
    
    from app.routes.dashboard import dashboard
    app.register_blueprint(dashboard)

    from app.routes.logs import logs
    app.register_blueprint(logs)

    from app.routes.alerts import alerts
    app.register_blueprint(alerts)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403
    
    return app