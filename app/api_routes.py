# app/api_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from .models import db, User, Card, UserCollection, Type, Set, Rarity
from sqlalchemy import cast, Integer, func
import logging # Hinzufügen für besseres Logging

# Erstellen eines Blueprints für die API
api = Blueprint('api', __name__, url_prefix='/api')

# --- Authentifizierungsendpunkte ---
# (Die /register und /login Routen bleiben unverändert)

@api.route('/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "Benutzername und Passwort sind erforderlich"}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "Benutzername existiert bereits"}), 409
    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username}), 201

@api.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "Benutzername und Passwort sind erforderlich"}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Ungültiger Benutzername oder Passwort"}), 401

# --- Öffentliche Karten-Endpunkte ---
# (Die /cards Endpunkte bleiben unverändert)

@api.route('/cards', methods=['GET'])
def api_get_cards():
    query = Card.query
    search_name = request.args.get('name')
    if search_name:
        query = query.filter(Card.name.ilike(f'%{search_name}%'))
    page = request.args.get('page', 1, type=int)
    cards_paginated = query.order_by(
        Card.set_id, cast(func.substr(Card.number, 1, func.instr(Card.number, '/') - 1), Integer)
    ).paginate(page=page, per_page=20, error_out=False)
    cards_data = [card.to_dict() for card in cards_paginated.items]
    return jsonify({
        'cards': cards_data,
        'page': cards_paginated.page,
        'total_pages': cards_paginated.pages,
        'has_next': cards_paginated.has_next
    })

@api.route('/cards/<card_id>', methods=['GET'])
@jwt_required(optional=True)
def api_get_card_detail(card_id):
    card = Card.query.get_or_404(card_id)
    card_dict = card.to_dict()
    current_user_id = get_jwt_identity()
    in_collection = False
    if current_user_id:
        in_collection = UserCollection.query.filter_by(
            user_id=current_user_id, card_id=card.id
        ).first() is not None
    card_dict['in_collection'] = in_collection
    return jsonify(card_dict)

# --- Geschützte Sammlungs-Endpunkte (MIT KORREKTUREN) ---

@api.route('/collection', methods=['GET'])
@jwt_required()
def api_get_collection():
    current_user_id = get_jwt_identity()
    collection_items = UserCollection.query.filter_by(user_id=current_user_id).all()
    card_ids = [item.card_id for item in collection_items]
    cards = Card.query.filter(Card.id.in_(card_ids)).all()
    return jsonify([card.to_dict() for card in cards])

@api.route('/collection/add/<card_id>', methods=['POST'])
@jwt_required()
def api_add_to_collection(card_id):
    """Fügt eine Karte zur Sammlung des Benutzers hinzu."""
    try:
        # KORREKTUR: Verwende get_jwt() um auf die 'sub' (subject/identity) zuzugreifen.
        # Dies ist eine robustere Methode.
        claims = get_jwt()
        current_user_id = claims.get('sub')

        if not current_user_id:
            return jsonify({"msg": "Benutzer-Identität nicht im Token gefunden"}), 400

        if not Card.query.get(card_id):
            return jsonify({"msg": "Karte nicht gefunden"}), 404

        existing = UserCollection.query.filter_by(user_id=current_user_id, card_id=card_id).first()
        if existing:
            return jsonify({"msg": "Karte ist bereits in der Sammlung"}), 409

        new_item = UserCollection(user_id=current_user_id, card_id=card_id)
        db.session.add(new_item)
        db.session.commit()

        return jsonify({"msg": "Karte zur Sammlung hinzugefügt"}), 201
    except Exception as e:
        # Fügt eine Log-Nachricht hinzu, falls ein unerwarteter Fehler auftritt
        logging.error(f"Fehler beim Hinzufügen zur Sammlung: {e}")
        return jsonify({"msg": "Interner Serverfehler"}), 500


@api.route('/collection/remove/<card_id>', methods=['DELETE'])
@jwt_required()
def api_remove_from_collection(card_id):
    """Entfernt eine Karte aus der Sammlung des Benutzers."""
    claims = get_jwt()
    current_user_id = claims.get('sub')

    if not current_user_id:
        return jsonify({"msg": "Benutzer-Identität nicht im Token gefunden"}), 400

    item = UserCollection.query.filter_by(user_id=current_user_id, card_id=card_id).first_or_404()
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({"msg": "Karte aus der Sammlung entfernt"}), 200