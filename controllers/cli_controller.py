from datetime import date
from flask import Blueprint
from init import db, bcrypt
from models.user import User
from models.card import Card
from models.comment import Comment


db_commands = Blueprint('db', __name__)


@db_commands.cli.command('create')
def create_tables():
    db.create_all()
    print("Tables created successfully")


@db_commands.cli.command('seed')
def seed_tables():
    users = [
        User(
            
            email="admin@gmail.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
            is_admin=True
        ),
        User(
            name="user1",
            email="user1@gmail.com",
            password=bcrypt.generate_password_hash('123456').decode('utf-8'),
           
        ),

    ]

    cards = [
        Card(
            title="Card11",
            description="description of Card 1",
            date=date.today(),
            status="To Do",
            priority="high",
            user = users[0]

        ),
        Card(
            title="Card2",
            description="description of Card 2",
            date=date.today(),
            status="Ongoing",
            priority="high",
            user = users[0]
        ),
           Card(
            title="Card3",
            description="description of Card 3",
            date=date.today(),
            status="Ongoing",
            priority="medium",
            user = users[1]
        ),
           Card(
            title="Card4",
            description="description of Card 4",
            date=date.today(),
            status="Done",
            priority="low",
            user = users[1]
        ),
    ]

    comments = [
        Comment(
            message="Comment 1",
            user = users[0],
            card = cards[0]
        ),
        Comment(
            message="Comment 2",
            user = users[0],
            card = cards[2]
        ),
        Comment(
            message="Comment 3",
            user = users[1],
            card = cards[3]
        ),
        Comment(
            message="Comment 4",
            user = users[1],
            card = cards[2]
        )
    ]

    db.session.add_all(users)
    db.session.add_all(cards)
    db.session.add_all(comments)


    db.session.commit()
    print("Tables seeded successfully")

@db_commands.cli.command('drop')
def drop_tables():
    db.drop_all()
    print("Tables dropped successfully")

