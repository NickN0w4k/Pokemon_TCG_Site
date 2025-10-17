# app/routes.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Card, Type, Set, Rarity, UserCollection, SetEra
from .forms import LoginForm, RegistrationForm
from sqlalchemy import cast, Integer, func

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Lade alle Äras und die zugehörigen Sets, sortiert nach dem Erscheinungsdatum der Sets.
    # `subqueryload` lädt die Sets und die dazugehörigen Karten effizient zusammen mit den Äras.
    eras = SetEra.query.options(
        db.subqueryload(SetEra.sets).joinedload(Set.cards)
    ).order_by(SetEra.id).all()

    # Sortiere die Sets für jede Ära manuell in Python, um den TypeError zu vermeiden.
    # Sets ohne release_date werden ans Ende sortiert.
    for era in eras:
        era.sets.sort(key=lambda s: (s.release_date is None, s.release_date))

    return render_template('index.html', eras=eras)

@main.route('/cards')
def card_search():
    # Basis-Query für alle Karten
    query = Card.query

    # Filter-Logik
    search_name = request.args.get('name')
    selected_type = request.args.get('type')
    selected_set = request.args.get('set')
    selected_rarity = request.args.get('rarity')

    if search_name:
        query = query.filter(Card.name.ilike(f'%{search_name}%'))
    if selected_type:
        query = query.join(Card.types).filter(Type.id == selected_type)
    if selected_set:
        query = query.filter(Card.set_id == selected_set)
    if selected_rarity:
        query = query.filter(Card.rarity_id == selected_rarity)

    # Paginierung für bessere Performance
    page = request.args.get('page', 1, type=int)
    # Sortiere nach Set und dann numerisch nach der Kartennummer.
    # CAST(SUBSTR(number, 1, INSTR(number, '/') - 1) AS INTEGER) extrahiert die Zahl vor dem '/'
    # und behandelt sie als Integer für die Sortierung.
    cards = query.order_by(Card.set_id, cast(func.substr(Card.number, 1, func.instr(Card.number, '/') - 1), Integer)).paginate(page=page, per_page=20, error_out=False)

    # API-Antwort: Wenn der Client JSON akzeptiert (z.B. unsere zukünftige App)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        user_collection_ids = set()
        if current_user.is_authenticated:
            user_collection_ids = {item.card_id for item in UserCollection.query.filter_by(user_id=current_user.id).all()}
        
        cards_data = []
        for card in cards.items:
            card_dict = card.to_dict()
            card_dict['in_collection'] = card.id in user_collection_ids
            cards_data.append(card_dict)

        return jsonify({
            'cards': cards_data,
            'page': cards.page,
            'total_pages': cards.pages,
            'has_next': cards.has_next
        })

    # Daten für die Filter-Dropdowns laden
    types = Type.query.order_by(Type.name).all()
    sets = Set.query.order_by(Set.release_date.desc()).all()
    rarities = Rarity.query.order_by(Rarity.name).all()
    user_collection_ids = set()
    if current_user.is_authenticated:
        user_collection_ids = {item.card_id for item in UserCollection.query.filter_by(user_id=current_user.id).all()}

    return render_template('card_search.html', cards=cards, types=types, sets=sets, rarities=rarities, user_collection_ids=user_collection_ids)

@main.route('/card_modal/<card_id>')
def card_modal(card_id):
    """Liefert den HTML-Inhalt für das Kartendetail-Modal."""
    card = Card.query.get_or_404(card_id)
    
    in_collection = False
    if current_user.is_authenticated:
        in_collection = UserCollection.query.filter_by(user_id=current_user.id, card_id=card.id).first() is not None

    # API-Antwort
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        card_dict = card.to_dict()
        card_dict['in_collection'] = in_collection
        return jsonify(card_dict)

    # Rendert nur das Inhalts-Template, nicht die ganze Seite
    return render_template('_card_modal_content.html', card=card, in_collection=in_collection)

@main.route('/collection/add/<card_id>', methods=['POST'])
@login_required
def add_to_collection(card_id):
    card = Card.query.get_or_404(card_id)
    
    # Prüfen, ob die Karte bereits in der Sammlung ist
    existing = UserCollection.query.filter_by(user_id=current_user.id, card_id=card.id).first()
    if not existing:
        new_item = UserCollection(user_id=current_user.id, card_id=card.id)
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'success': True, 'message': f'"{card.name}" wurde hinzugefügt.', 'action': 'added'}), 200
    else:
        # 409 Conflict ist der passende HTTP-Statuscode, wenn eine Ressource bereits existiert.
        return jsonify({'success': False, 'message': f'"{card.name}" ist bereits in der Sammlung.'}), 409

@main.route('/collection/remove/<card_id>', methods=['POST'])
@login_required
def remove_from_collection(card_id):
    item = UserCollection.query.filter_by(user_id=current_user.id, card_id=card_id).first_or_404()
    card_name = item.card.name
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True, 'message': f'"{card_name}" wurde entfernt.', 'action': 'removed'}), 200

@main.route('/collection')
@login_required
def collection():
    # 1. Hole alle card_ids aus der Sammlung des Benutzers (aus der users_db).
    collection_items = UserCollection.query.filter_by(user_id=current_user.id).all()
    card_ids = [item.card_id for item in collection_items]

    # Query, um alle Karten der Sammlung zu laden
    cards_query = Card.query.options(
        db.joinedload(Card.set).joinedload(Set.era)
    ).filter(Card.id.in_(card_ids)).order_by(
        Card.set_id, cast(func.substr(Card.number, 1, func.instr(Card.number, '/') - 1), Integer)
    )

    # API-Antwort: Eine flache Liste aller Karten in der Sammlung
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify([card.to_dict() for card in cards_query.all()])

    # Web-Antwort: Gruppiere die Karten für die Template-Anzeige
    cards = cards_query.all()
    collection_by_era = group_cards_by_era_and_set(cards)
    return render_template('collection.html', collection_by_era=collection_by_era, total_cards=len(card_ids))

def group_cards_by_era_and_set(cards):
    """Hilfsfunktion, um eine Liste von Karten nach Ära und Set zu gruppieren."""
    collection_by_era = {}
    for card in cards:
        era, set_ = card.set.era, card.set
        collection_by_era.setdefault(era, {}).setdefault(set_, []).append(card)
    return collection_by_era

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Ungültiger Benutzername oder Passwort', 'danger')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        flash('Erfolgreich angemeldet!', 'success')
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Anmelden', form=form)

@main.route('/logout')
def logout():
    logout_user()
    flash('Du wurdest abgemeldet.', 'info')
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Glückwunsch, du bist jetzt registriert!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Registrieren', form=form)