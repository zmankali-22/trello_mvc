from datetime import timedelta

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token
from psycopg2 import errorcodes

from init import db, bcrypt
from models.user import User, user_schema

auth_bp = Blueprint('auth',__name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        # data we get from  the body of the request
        body_data = request.get_json()
    #  create the user instance
        user = User(
            name=body_data.get('name'),
            email=body_data.get('email'),
        )
        # password from the request body
        password = body_data.get('password')
        # if password exist, hash the paasword
        if password:
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
    #  add and commit the user to DB
        db.session.add(user)
        db.session.commit()
        # respond back to cliend
        return user_schema.dump(user), 201
    
    except IntegrityError as err:
        print(err.orig.pgcode)
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name}  is required"}
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {'error': 'Email address  already exists'}, 409
        
@auth_bp.route("/login", methods=["POST"])
def auth_login():
    # get the data from the request body
    body_data = request.get_json()
    # find the user with email address
    stmt = db.select(User).filter_by(email=body_data.get('email'))
    user = db.session.scalar(stmt)
    # if the user exists and password is correct
    if user and bcrypt.check_password_hash(user.password, body_data.get('password')):
        # create jwt token
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        # return the token along with the user
        return {"email": user.email, "token":token, "is_admin": user.is_admin }
    
    # else
    else:
        # return error message
        return {"error": "Invalid email or password"}, 401
    