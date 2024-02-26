from flask import Blueprint, request
from datetime import date

from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.card import Card, cards_schema, card_schema
from controllers.comment_controller import comments_bp
from models.user import User

cards_bp = Blueprint('cards', __name__, url_prefix='/cards')
cards_bp.register_blueprint(comments_bp)

@cards_bp.route('/')
def get_all_cards():
    stmt = db.select(Card).order_by(Card.date.desc())
    cards = db.session.scalars(stmt)
    return cards_schema.dump(cards)

@cards_bp.route('/<int:card_id>')
def get_one_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card :
        return card_schema.dump(card)
    else:
        return {'error': f"Card {card_id} not found"}, 404
    

@cards_bp.route('/', methods=['POST'])
@jwt_required()
def create_card():
    
    # data we get from  the body of the request
    body_data = card_schema.load(request.get_json())
#  create the cardinstance
    card = Card(
        title=body_data.get('title'),
        description=body_data.get('description'),
        date = date.today(),
        status=body_data.get('status'),
        priority=body_data.get('priority'),
        user_id = get_jwt_identity()
    )

    db.session.add(card)
    db.session.commit()

    return card_schema.dump(card), 201


@cards_bp.route('/<int:card_id>/', methods=['DELETE'])
@jwt_required()
def delete_card(card_id):
    is_admin = is_user_admin()
    if not is_admin:
        return {'error': 'You are not authorized to delete'}, 403
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card :
        db.session.delete(card)
        db.session.commit()
        return {"message": f"Card '{card.title}' deleted successfully"}
    else:
        return {'error': f"Card {card_id} not found"}, 404

@cards_bp.route('/<int:card_id>', methods=['PUT','PATCH' ])
@jwt_required()
def update_card(card_id):
   

    # data we get from  the body of the request
    body_data = card_schema.load(request.get_json(), partial=True)
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card :
        if str(card.user_id) != get_jwt_identity():
            return {"error": "Only the owner can edit the card"}, 403
        card.title = body_data.get('title') or card.title
        card.description = body_data.get('description') or card.description
        card.status = body_data.get('status') or card.status
        card.priority = body_data.get('priority') or card.priority

        db.session.commit()
        return card_schema.dump(card)
    else:
        return {'error': f"Card {card_id} not found"}, 404


def is_user_admin():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user.is_admin
 