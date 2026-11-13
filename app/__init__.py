from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from flask import Flask
from dotenv import load_dotenv

from .config import BASE_DIR, settings


def create_app(test_config=None):
    load_dotenv(BASE_DIR / ".env", override=False)
    app = Flask(__name__)
    app.config.from_mapping(settings())
    if test_config:
        app.config.update(test_config)
    from .routes import bp
    app.register_blueprint(bp)

    css_version = sha256((Path(app.static_folder) / 'css/style.css').read_bytes()).hexdigest()[:12]

    @app.context_processor
    def shared_context():
        return {'year': datetime.now(timezone.utc).year, 'css_version': css_version}

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; img-src 'self'; style-src 'self'; "
            "font-src 'self'; script-src 'none'; object-src 'none'; "
            "base-uri 'self'; frame-ancestors 'none'; form-action 'none'"
        )
        return response

    return app
