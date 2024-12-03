from flask import Blueprint, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import json

SWAGGER_URL = '/api/docs'
API_URL = '/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Repositorio UNSA API"
    }
)

swagger_bp = Blueprint('swagger_bp', __name__)
@swagger_bp.route('/swagger.json')
def serve_swagger_json():
    with open('app/static/swagger.json', 'r') as file:
        swagger_data = json.load(file)
        swagger_data['host'] = request.host
        swagger_data['schemes'] = ['https' if request.is_secure else 'http']
        return jsonify(swagger_data)