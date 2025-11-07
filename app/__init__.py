from flask import Flask
from flask_cors import CORS
from .config import Config
from .models import db
from .views import views


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/*": {"origins": "*"}})
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(views)
    return app
