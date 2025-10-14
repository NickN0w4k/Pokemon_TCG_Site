# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .models import db, User
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ein-sehr-geheimer-schluessel' # Ändern für Produktion!
    
    # Basisverzeichnis des Projekts (wo sich die 'run.py' befindet)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Standard-Datenbank für die Kartendaten
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'pokemon_cards.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Zusätzliche Datenbank für Benutzer und Sammlungen
    app.config['SQLALCHEMY_BINDS'] = {
        'users_db': 'sqlite:///' + os.path.join(base_dir, 'users.db')
    }

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login' # Weiterleitung, wenn nicht angemeldet
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Routen registrieren
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
