from flask import Blueprint, request
from datetime import date

from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.card import Card, cards_schema, card_schema
from models.comment import Comment, comment_schema

cards_bp = Blueprint('cards', __name__, url_prefix='/cards')

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
    body_data = request.get_json()
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

def delete_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card :
        db.session.delete(card)
        db.session.commit()
        return {"message": f"Card '{card.title}' deleted successfully"}
    else:
        return {'error': f"Card {card_id} not found"}, 404

@cards_bp.route('/<int:card_id>', methods=['PUT','PATCH' ])
def update_card(card_id):

    # data we get from  the body of the request
    body_data = request.get_json()
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card :
        card.title = body_data.get('title') or card.title
        card.description = body_data.get('description') or card.description
        card.status = body_data.get('status') or card.status
        card.priority = body_data.get('priority') or card.priority

        db.session.commit()
        return card_schema.dump(card)
    else:
        return {'error': f"Card {card_id} not found"}, 404

# comments

@cards_bp.route('/<int:card_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(card_id):

    # data we get from  the body of the request
    body_data = request.get_json()
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        comment = Comment(
            message=body_data.get('message'),
            user_id=get_jwt_identity(),
            card=card
        )
        db.session.add(comment)
        db.session.commit()
        return comment_schema.dump(comment), 201
    else:
        return {'error': f"Card with {card_id} not found"}, 404
    
@cards_bp.route('/<int:card_id>/comments/<comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(card_id, comment_id):
        stmt = db.select(Comment).filter_by(id=comment_id)
        comment = db.session.scalar(stmt)
        if comment and comment.card.id == card_id:
            db.session.delete(comment)
            db.session.commit()
            return {"message": f"Comment with {comment_id}'{comment.message}' deleted successfully"}
        else:
            return {'error': f"Comment  with id {comment_id} not found in card with id {card_id}"}, 404


@cards_bp.route('/<int:card_id>/comments/<int:comment_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_comment(card_id, comment_id):

    # data we get from  the body of the request
    body_data = request.get_json()
    stmt = db.select(Comment).filter_by(id=comment_id, card_id=card_id)
    comment = db.session.scalar(stmt)
    if comment :
        comment.message = body_data.get('message') or comment.message
        db.session.commit()
        return comment_schema.dump(comment)
    else:
        return {'error': f"Comment  with id {comment_id} not found in card with id {card_id}"}, 404
