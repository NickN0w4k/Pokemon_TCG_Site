# app/models.py
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# --- Verbindungstabellen für N-zu-N Beziehungen ---

card_types = db.Table('card_types',
    db.Column('card_id', db.Text, db.ForeignKey('cards.id'), primary_key=True),
    db.Column('type_id', db.Integer, db.ForeignKey('types.id'), primary_key=True)
)

card_subtypes = db.Table('card_subtypes',
    db.Column('card_id', db.Text, db.ForeignKey('cards.id'), primary_key=True),
    db.Column('subtype_id', db.Integer, db.ForeignKey('subtypes.id'), primary_key=True)
)

# --- Assoziationsobjekte für N-zu-N mit Zusatzdaten ---

class CardWeakness(db.Model):
    __tablename__ = 'card_weaknesses'
    card_id = db.Column(db.Text, db.ForeignKey('cards.id'), primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'), primary_key=True)
    value = db.Column(db.Text)
    type = db.relationship("Type")

    def to_dict(self):
        return {
            'type': self.type.name,
            'value': self.value
        }

class CardResistance(db.Model):
    __tablename__ = 'card_resistances'
    card_id = db.Column(db.Text, db.ForeignKey('cards.id'), primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'), primary_key=True)
    value = db.Column(db.Text)
    type = db.relationship("Type")

    def to_dict(self):
        return {
            'type': self.type.name,
            'value': self.value
        }

# --- Nachschlage-Tabellen (Lookup Tables) ---

class SetEra(db.Model):
    __tablename__ = 'set_eras'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    sets = db.relationship('Set', backref='era', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Set(db.Model):
    __tablename__ = 'sets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    era_id = db.Column(db.Integer, db.ForeignKey('set_eras.id'))
    release_date = db.Column(db.Text)
    cards = db.relationship('Card', backref='set', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'release_date': self.release_date,
            'era': self.era.name if self.era else None
        }

class Rarity(db.Model):
    __tablename__ = 'rarities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    cards = db.relationship('Card', backref='rarity', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Type(db.Model):
    __tablename__ = 'types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    def to_dict(self):
        return { 'name': self.name }

class Subtype(db.Model):
    __tablename__ = 'subtypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

# --- Zentrale Tabelle: Card ---

class Card(db.Model):
    __tablename__ = 'cards'
    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    supertype = db.Column(db.Text, nullable=False)
    hp = db.Column(db.Integer)
    evolvesFrom = db.Column(db.Text)
    artist = db.Column(db.Text)
    image_path = db.Column(db.Text, nullable=False)
    number = db.Column(db.Text)
    set_id = db.Column(db.Integer, db.ForeignKey('sets.id'))
    rarity_id = db.Column(db.Integer, db.ForeignKey('rarities.id'))

    # Beziehungen
    types = db.relationship('Type', secondary=card_types, lazy='subquery',
                            backref=db.backref('cards', lazy=True))
    subtypes = db.relationship('Subtype', secondary=card_subtypes, lazy='subquery',
                               backref=db.backref('cards', lazy=True))
    attacks = db.relationship('Attack', backref='card', lazy=True, cascade="all, delete-orphan")
    abilities = db.relationship('Ability', backref='card', lazy=True, cascade="all, delete-orphan")
    rules = db.relationship('Rule', backref='card', lazy=True, cascade="all, delete-orphan")
    weaknesses = db.relationship('CardWeakness', backref='card', lazy='joined', cascade="all, delete-orphan")
    resistances = db.relationship('CardResistance', backref='card', lazy='joined', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'supertype': self.supertype,
            'hp': self.hp,
            'evolvesFrom': self.evolvesFrom,
            'artist': self.artist,
            'image_path': url_for('static', filename=self.image_path, _external=True),
            'number': self.number,
            'set': self.set.to_dict() if self.set else None,
            'rarity': self.rarity.name if self.rarity else None,
            'types': [t.name for t in self.types],
            'subtypes': [st.name for st in self.subtypes],
            'attacks': [attack.to_dict() for attack in self.attacks],
            'abilities': [ability.to_dict() for ability in self.abilities],
            'rules': [rule.rule_text for rule in self.rules],
            'weaknesses': [weakness.to_dict() for weakness in self.weaknesses],
            'resistances': [resistance.to_dict() for resistance in self.resistances]
        }


# --- Benutzer-Modell ---
# Vorerst einfach gehalten für die manuelle Anlage

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    __bind_key__ = 'users_db'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- Sammlungstabelle ---
class UserCollection(db.Model):
    __bind_key__ = 'users_db'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_id = db.Column(db.Text, nullable=False)
    
    user = db.relationship('User', backref=db.backref('collection_items', lazy=True))
    card = db.relationship(
        'Card',
        primaryjoin="UserCollection.card_id == Card.id",
        foreign_keys=[card_id],
        backref=db.backref('collection_items', lazy=True)
    )


# --- Eigenschafts-Tabellen ---
class Attack(db.Model):
    __tablename__ = 'attacks'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Text, db.ForeignKey('cards.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    damage = db.Column(db.Text)
    text = db.Column(db.Text)
    costs = db.relationship('AttackCost', backref='attack', lazy='joined', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'name': self.name,
            'damage': self.damage,
            'text': self.text,
            'costs': [cost.cost_type for cost in self.costs]
        }

class AttackCost(db.Model):
    __tablename__ = 'attack_costs'
    id = db.Column(db.Integer, primary_key=True)
    attack_id = db.Column(db.Integer, db.ForeignKey('attacks.id'), nullable=False)
    cost_type = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'cost_type': self.cost_type
        }

class Ability(db.Model):
    __tablename__ = 'abilities'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Text, db.ForeignKey('cards.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text)
    type = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'name': self.name,
            'text': self.text,
            'type': self.type
        }

class Rule(db.Model):
    __tablename__ = 'rules'
    card_id = db.Column(db.Text, db.ForeignKey('cards.id'), primary_key=True)
    rule_text = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return { 'rule_text': self.rule_text }
