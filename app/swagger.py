from flask import Blueprint, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import json
import os

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

# Función para modificar el swagger.json en tiempo de ejecución
def swagger_json_processor():
    with open('app/static/swagger.json', 'r') as file:
        swagger_data = json.load(file)
        # Obtener el host dinámicamente
        swagger_data['host'] = request.host
        # Actualizar schemes según el protocolo
        swagger_data['schemes'] = ['https' if request.is_secure else 'http']
        return swagger_data

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Repositorio UNSA API"
    }
)

@swaggerui_blueprint.route('/static/swagger.json')
def serve_swagger_json():
    return jsonify(swagger_json_processor())