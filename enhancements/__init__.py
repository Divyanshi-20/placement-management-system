# enhancements/__init__.py
from .routes import enhancements_bp
from .db import close_db

def init_app(app):
    """Register blueprint and teardown DB close"""
    app.register_blueprint(enhancements_bp)
    app.teardown_appcontext(close_db)

# keep name `init_app` — app.py imports it as init_enhancements
