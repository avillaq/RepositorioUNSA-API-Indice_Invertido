import socket
import json
from flask import jsonify, request
from app.api.models import Documento, Coleccion, Autor, Documento_Autor, PalabraClave, Documento_PalabraClave, Editor
from app.api import bp
from app.extensions import db, limiter, cache

# Configuracion del servidor C++ de índice invertido
INDICE_INVERTIDO_HOST = "localhost"
INDICE_INVERTIDO_PORT = 8081

@bp.route('/documentos', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_documentos():
    titulo = request.args.get('titulo')
    fecha = request.args.get('fecha')
    id_autor = request.args.get('id_autor', type=int)
    id_coleccion = request.args.get('id_coleccion', type=int)
    id_editor = request.args.get('id_editor', type=int)
    id_palabra_clave = request.args.get('id_palabra_clave', type=int)

    # Parametros para ordenar
    sort = request.args.get('sort', 'titulo')  # Por defecto es el título
    order = request.args.get('order', 'asc')  # Por defecto en orden ascendente

    # Paginación
    page = request.args.get('page', 1, type=int)  # Página actual. 1 por defecto
    limit = request.args.get('limit', 10, type=int)  # Resultados por página. 10 por defecto

    documentos = Documento.query

    # Filtrar la consulta
    if titulo:
        documentos = documentos.filter(Documento.titulo.like(f'%{titulo}%'))
    if fecha:
        documentos = documentos.filter_by(fecha=fecha)
    if id_coleccion:
        documentos = documentos.filter_by(id_coleccion=id_coleccion)
    if id_editor:
        documentos = documentos.filter_by(id_editor=id_editor)
    if id_autor:
        documentos = documentos.join(Documento_Autor, Documento.id_documento == Documento_Autor.id_documento).filter(Documento_Autor.id_autor == id_autor)
    if id_palabra_clave:
        documentos = documentos.join(Documento_PalabraClave, Documento.id_documento == Documento_PalabraClave.id_documento).filter(Documento_PalabraClave.id_palabra_clave == id_palabra_clave)
        
    # Ordenar la consulta
    if sort in ['titulo', 'fecha']:
        if order == 'desc':
            documentos = documentos.order_by(db.desc(getattr(Documento, sort)))
        else:
            documentos = documentos.order_by(getattr(Documento, sort))

    # Aplicar paginación
    documentos_paginados = documentos.paginate(page=page, per_page=limit)

    resultado = {
        'page': documentos_paginados.page,
        'total_pages': documentos_paginados.pages,
        'total_items': documentos_paginados.total,
        'items': [documento.format() for documento in documentos_paginados.items]
    }
    return jsonify(resultado)

@bp.route('/documentos/<int:id>/', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_documento(id):
    documento = Documento.query.get_or_404(id)
    return jsonify(documento.format())

@bp.route('/documentos/<int:id>/palabras_clave', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_palabras_clave_de_documento(id):
    documento = Documento.query.get_or_404(id)

    # Ordenar
    order = request.args.get('order', 'asc')  # Por defecto en orden ascendente

    palabras_clave = PalabraClave.query.join(Documento_PalabraClave, Documento_PalabraClave.id_palabra_clave == PalabraClave.id_palabra_clave).filter(Documento_PalabraClave.id_documento == documento.id_documento)

    # Ordenar la consulta
    if order == 'desc':
        palabras_clave = palabras_clave.order_by(db.desc(PalabraClave.palabra_clave))
    else:
        palabras_clave = palabras_clave.order_by(PalabraClave.palabra_clave)

    resultado = {
        'total_items': len(palabras_clave.all()),
        'items': [palabra_clave.format() for palabra_clave in palabras_clave.all()]
    }   
    return jsonify(resultado)

@bp.route('/documentos/<int:id>/autores', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_autores_de_documento(id):
    documento = Documento.query.get_or_404(id)

    # Ordenar
    order = request.args.get('order', 'asc')  # Por defecto en orden ascendente
    
    autores = Autor.query.join(Documento_Autor, Documento_Autor.id_autor == Autor.id_autor).filter(Documento_Autor.id_documento == documento.id_documento)
            
    # Ordenar la consulta
    if order == 'desc':
        autores = autores.order_by(db.desc(Autor.nombre_autor))
    else:
        autores = autores.order_by(Autor.nombre_autor)
          
    resultado = {
        'total_items': len(autores.all()),
        'items': [autor.format() for autor in autores.all()]
    }
    return jsonify(resultado)

@bp.route('/colecciones', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_colecciones():
    nombre_coleccion = request.args.get('nombre_coleccion')

    # Parametros para ordenar
    order = request.args.get('order', 'asc')  # Por defecto en orden ascendente

    # Paginación
    page = request.args.get('page', 1, type=int)  # Página actual. 1 por defecto
    per_page = request.args.get('per_page', 10, type=int)  # Resultados por página. 10 por defecto

    colecciones = Coleccion.query

    # Filtrar la consulta
    if nombre_coleccion:
        colecciones = colecciones.filter(Coleccion.nombre_coleccion.like(f'%{nombre_coleccion}%'))

    # Ordenar la consulta
    if order == 'desc':
        colecciones = colecciones.order_by(db.desc(Coleccion.nombre_coleccion))
    else:
        colecciones = colecciones.order_by(Coleccion.nombre_coleccion)

    # Aplicar paginación
    colecciones_paginados = colecciones.paginate(page=page, per_page=per_page)

    resultado = {
        'page': colecciones_paginados.page,
        'total_pages': colecciones_paginados.pages,
        'total_items': colecciones_paginados.total,
        'items': [coleccion.format() for coleccion in colecciones_paginados.items]
    }
    return jsonify(resultado)

@bp.route('/colecciones/<int:id>/', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_coleccion(id):
    coleccion = Coleccion.query.get_or_404(id)
    return jsonify(coleccion.format())

@bp.route('/autores', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_autores():
    nombre_autor = request.args.get('nombre_autor')

    # Ordenar
    order = request.args.get('order', 'asc')  # Por defecto en orden ascendente

    # Paginación
    page = request.args.get('page', 1, type=int)  # Página actual. 1 por defecto
    limit = request.args.get('limit', 10, type=int)  # Resultados por página. 10 por defecto

    autores = Autor.query

    # Filtrar la consulta
    if nombre_autor:
        autores = autores.filter(Autor.nombre_autor.like(f'%{nombre_autor}%'))

    # Ordenar la consulta
    if order == 'desc':
        autores = autores.order_by(db.desc(Autor.nombre_autor))
    else:
        autores = autores.order_by(Autor.nombre_autor)

    # Aplicar paginación
    autores_paginados = autores.paginate(page=page, per_page=limit)

    resultado = {
        'page': autores_paginados.page,
        'total_pages': autores_paginados.pages,
        'total_items': autores_paginados.total,
        'items': [autor.format() for autor in autores_paginados.items]
    }
    return jsonify(resultado)

@bp.route('/autores/<int:id>/', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_autor(id):
    autor = Autor.query.get_or_404(id)
    return jsonify(autor.format())

@bp.route('/palabras_clave', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_palabras_clave():
    palabra_clave = request.args.get('palabra_clave')

    # Ordenar
    order = request.args.get('order', 'asc')  # Por defecto en orden ascendente

    # Paginación
    page = request.args.get('page', 1, type=int)  # Página actual. 1 por defecto
    limit = request.args.get('limit', 10, type=int)  # Resultados por página. 10 por defecto

    palabras_clave = PalabraClave.query

    # Filtrar la consulta
    if palabra_clave:
        palabras_clave = palabras_clave.filter(PalabraClave.palabra_clave.like(f'%{palabra_clave}%'))

    # Ordenar la consulta
    if order == 'desc':
        palabras_clave = palabras_clave.order_by(db.desc(PalabraClave.palabra_clave))
    else:
        palabras_clave = palabras_clave.order_by(PalabraClave.palabra_clave)

    # Aplicar paginación
    palabras_clave_paginados = palabras_clave.paginate(page=page, per_page=limit)

    resultado = {
        'page': palabras_clave_paginados.page,
        'total_pages': palabras_clave_paginados.pages,
        'total_items': palabras_clave_paginados.total,
        'items': [palabra_clave.format() for palabra_clave in palabras_clave_paginados.items]
    }
    return jsonify(resultado)

@bp.route('/palabras_clave/<int:id>/', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def get_palabra_clave(id):
    palabra_clave = PalabraClave.query.get_or_404(id)
    return jsonify(palabra_clave.format())

@bp.route('/editores', methods=['GET'])
@limiter.limit("10/minute")
def get_editores():
    editores = Editor.query.all()
    resultado = {
        'total_items': len(editores),
        'items': [editor.format() for editor in editores]
    }
    return jsonify(resultado)

@bp.route('/editores/<int:id>/', methods=['GET'])
@limiter.limit("10/minute")
def get_editor(id):
    editor = Editor.query.get_or_404(id)
    return jsonify(editor.format())

def consultar_indice_invertido(palabras):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((INDICE_INVERTIDO_HOST, INDICE_INVERTIDO_PORT))
        
        client_socket.sendall(palabras.encode('utf-8'))

        # Recibir la respuesta del servidor en fragmentos
        response = ""
        while True:
            part = client_socket.recv(8192).decode("utf-8")
            response += part
            if len(part) < 8192:
                break
        response_data = json.loads(response)
        
        client_socket.close()

        return response_data

    except Exception as e:
        return str(e)

@bp.route('/buscar', methods=['GET'])
@limiter.limit("10/minute")
@cache.cached(query_string=True)
def buscar_documentos():
    palabras = request.args.get('palabras', '').strip()
    if not palabras:
        return jsonify(error="Debe proporcionar palabras clave para buscar"), 400

    # Consultar al indice invertido
    respuesta = consultar_indice_invertido(palabras)

    try:
        resultado = {
            'total_items': respuesta["total"],
            'items': respuesta["resultados"]
        }
        return jsonify(resultado)

    except ValueError:
        return jsonify(error="Error procesando la respuesta del índice invertido"), 500

@bp.errorhandler(429)
def ratelimit_error(e):
    return jsonify(error="Rate limit exceeded", message=str(e.description)), 429

@bp.errorhandler(404)
def not_found_error(e):
    return jsonify(error="Not found", message=str(e.description)), 404

@bp.route('/')
def index():
    return jsonify(message="Welcome to the API")