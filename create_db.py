# create_db.py
from app import create_app
from app.models import db

# Erstellt eine Instanz der Flask-Anwendung
app = create_app()

# Der 'app_context' stellt sicher, dass die Anwendungskonfiguration
# (wie z.B. die Datenbank-Pfade) geladen ist.
with app.app_context():
    print("Erstelle alle Datenbank-Tabellen...")
    
    # db.create_all() liest alle Model-Klassen und erstellt die Tabellen.
    # Es respektiert den '__bind_key__', um die Tabellen in der richtigen DB anzulegen.
    db.create_all()
    
    print("Datenbanken und Tabellen erfolgreich erstellt!")