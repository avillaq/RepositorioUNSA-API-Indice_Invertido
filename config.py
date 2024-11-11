import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost:3306/repositorio_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24) # Recomendacion: usar variable de entorno
