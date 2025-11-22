from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from nira.config import Config

# Keep extensions unbound so tests and the app factory share one setup.
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprints
    from nira.appointments import appointments_bp
    app.register_blueprint(appointments_bp)

    # Ensure tables exist for simple deployments without migrations.
    with app.app_context():
        db.create_all()

    return app
