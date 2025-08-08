from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .base import BaseModel
from app.extensions import db

@BaseModel.register('User')
class User(BaseModel, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    pw_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, **kwargs):
        # Call parent's __init__ first
        super().__init__(**kwargs)
        # Handle password hashing if password is provided
        if 'password' in kwargs:
            self.set_password(kwargs['password'])

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username
        }

