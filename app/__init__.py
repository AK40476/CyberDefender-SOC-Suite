from flask import Flask


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dev-secret-key-change-later"

    @app.route("/")
    def home():
        return """
        <h1>🛡️ CyberDefender SOC Suite</h1>
        <p>Security Operations Center Platform</p>
        <p>Status: System Online</p>
        """

    return app