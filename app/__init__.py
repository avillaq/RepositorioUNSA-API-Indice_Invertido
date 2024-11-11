from flask import Flask
from app.extensions import db, limiter, cache
from app.swagger import swaggerui_blueprint, SWAGGER_URL
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Registrar los Blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Registrar Swagger UI
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
