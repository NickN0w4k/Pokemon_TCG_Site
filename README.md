# Pokémon TCG Collection Manager

Dieses Projekt ist eine Webanwendung zur Verwaltung einer Sammlung von Pokémon-Sammelkarten. Benutzer können nach Karten suchen, sie zu ihrer Sammlung hinzufügen und ihre Sammlung online einsehen.

## Features

*   **Kartensuche:** Durchsuchen Sie eine Datenbank von Pokémon-Karten.
*   **Benutzer-Authentifizierung:** Erstellen Sie ein Konto und melden Sie sich an, um Ihre persönliche Sammlung zu verwalten.
*   **Sammlungsverwaltung:** Fügen Sie Karten zu Ihrer Sammlung hinzu oder entfernen Sie sie.
*   **REST-API:** Eine API zur programmatischen Abfrage von Kartendaten und zur Verwaltung von Sammlungen (geschützt durch JWT).
*   **Detailansicht:** Sehen Sie sich detaillierte Informationen zu jeder Karte an.

## Technologies Used

*   **Backend:** Python, Flask
*   **Datenbank:** SQLAlchemy, SQLite
*   **Frontend:** HTML, CSS, JavaScript, Jinja2
*   **Authentifizierung:** Flask-Login (für Web), Flask-JWT-Extended (für API)
*   **Formulare:** Flask-WTF

## Setup and Installation

Folgen Sie diesen Schritten, um die Anwendung lokal auszuführen.

### 1. Klonen Sie das Repository

```bash
git clone <repository-url>
cd Pokemon_TCG_Site
```

### 2. Erstellen Sie eine virtuelle Umgebung

Es wird dringend empfohlen, eine virtuelle Umgebung zu verwenden, um die Projektabhängigkeiten zu isolieren.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installieren Sie die Abhängigkeiten

Installieren Sie alle erforderlichen Pakete aus der `requirements.txt`-Datei.

```bash
pip install -r requirements.txt
```

### 4. Erstellen Sie die Datenbank

Führen Sie das Skript `create_db.py` aus, um die SQLite-Datenbanken (`pokemon_cards.db` und `users.db`) und die erforderlichen Tabellen zu erstellen.

```bash
python create_db.py
```

Stellen Sie sicher, dass die `pokemon_cards.db` im Hauptverzeichnis des Projekts vorhanden ist. Diese Datenbank wird von der Anwendung für die Kartendaten verwendet, aber ihre Erstellung ist nicht Teil dieses Repositorys.

## Running the Application

Starten Sie die Flask-Entwicklungsserver mit dem folgenden Befehl:

```bash
python run.py
```

Die Anwendung ist dann unter `http://127.0.0.1:5000` in Ihrem Webbrowser erreichbar.

## Datenbank

Das Projekt verwendet zwei SQLite-Datenbanken:

1.  `pokemon_cards.db`: Enthält alle Daten der Pokémon-Karten. Diese Datei wird nicht vom `create_db.py`-Skript generiert, sondern muss vorhanden sein.
2.  `users.db`: Speichert Benutzerinformationen (Benutzernamen, Passwörter). Diese wird vom `create_db.py`-Skript erstellt.

Das Datenbankschema für die Kartendatenbank ist in `DATABASE_SCHEMA.md` dokumentiert.

## Projektstruktur

```
.
├── app/                  # Hauptanwendungs-Paket
│   ├── static/           # Statische Dateien (CSS, JS, Bilder)
│   ├── templates/        # HTML-Vorlagen (Jinja2)
│   ├── __init__.py       # Application Factory
│   ├── api_routes.py     # Routen für die REST-API
│   ├── forms.py          # WTForms-Formulare
│   ├── models.py         # SQLAlchemy-Datenbankmodelle
│   └── routes.py         # Haupt-Web-Routen
├── instance/             # Instanz-Ordner (kann DB-Dateien enthalten)
├── venv/                 # Virtuelle Umgebung
├── .gitignore
├── config.py             # Konfigurationsdatei
├── create_db.py          # Skript zur DB-Erstellung
├── DATABASE_SCHEMA.md    # Dokumentation des DB-Schemas
├── pokemon_cards.db      # Haupt-Kartendatenbank
├── requirements.txt      # Python-Abhängigkeiten
└── run.py                # Startpunkt der Anwendung
```

