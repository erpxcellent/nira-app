from flask import Flask, session, g, request
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

    @app.before_request
    def set_language():
        lang = session.get("lang", config_class.DEFAULT_LANG)
        if lang not in config_class.AVAILABLE_LANGS:
            lang = config_class.DEFAULT_LANG
        g.current_lang = lang

    @app.context_processor
    def inject_language():
        return {
            "current_lang": getattr(g, "current_lang", config_class.DEFAULT_LANG),
            "available_langs": config_class.AVAILABLE_LANGS,
        }

    # Blueprints
    from nira.appointments import appointments_bp
    app.register_blueprint(appointments_bp)

    # Ensure tables exist for simple deployments without migrations.
    with app.app_context():
        db.create_all()

    return app
