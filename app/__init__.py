# app/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager

# Initialisierung der Erweiterungen außerhalb der Factory, 
# um sie global zugänglich zu machen.
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """
    Erstellt und konfiguriert eine Instanz der Flask-Anwendung.
    Dieses Muster wird als "Application Factory" bezeichnet.
    """
    app = Flask(__name__)

    # --- Konfiguration ---
    # Setzt einen geheimen Schlüssel, der für Sessions und andere Sicherheitsfeatures
    # benötigt wird. Ändern Sie diesen in einer Produktionsumgebung!
    app.config['SECRET_KEY'] = 'ihr-super-geheimer-web-schluessel'
    
    # Setzt den geheimen Schlüssel für die JWT-Token-Signierung.
    # Dieser sollte ebenfalls einzigartig und geheim sein.
    app.config['JWT_SECRET_KEY'] = 'ihr-noch-geheimerer-jwt-schluessel'

    # Bestimmt den Basispfad des Projekts
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # Konfiguriert die Datenbanken.
    # Haupt-DB für Kartendaten.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, '..', 'pokemon_cards.db')
    # Separate DB für Benutzerdaten.
    app.config['SQLALCHEMY_BINDS'] = {
        'users_db': 'sqlite:///' + os.path.join(base_dir, '..', 'users.db')
    }
    # Deaktiviert eine ressourcenintensive Funktion von SQLAlchemy, die nicht benötigt wird.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Initialisierung der Erweiterungen mit der App ---
    db.init_app(app)
    login_manager.init_app(app)
    jwt = JWTManager(app)

    # --- Blueprints registrieren ---
    # Ein Blueprint ist eine Sammlung von Routen, die die Anwendung strukturieren.
    
    # Registriert die Routen für die Webseite (z.B. '/', '/login')
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Registriert die Routen für die API (z.B. '/api/cards', '/api/login')
    from .api_routes import api as api_blueprint
    app.register_blueprint(api_blueprint)

    # --- Konfiguration für Flask-Login (Web-Authentifizierung) ---
    # Leitet unauthentifizierte Benutzer zur Login-Seite weiter.
    login_manager.login_view = 'main.login'
    # Setzt die Bootstrap-Kategorie für Flash-Nachrichten.
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        """
        Diese Funktion wird von Flask-Login verwendet, um den aktuellen Benutzer
        aus der Datenbank zu laden, basierend auf der ID in der Session.
        """
        from .models import User
        # Die user_id aus der Session ist ein String, also muss sie in einen Integer umgewandelt werden.
        return User.query.get(int(user_id))

    return app