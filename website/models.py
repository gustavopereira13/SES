from bson import json_util
from flask_login import UserMixin
from flask import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    files = db.relationship('File')


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(10000))
    file_location = db.Column(db.String(10000))
    file_owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_date = db.Column(db.DateTime(timezone=True), default=func.now())


def get_user(self, user_id):
    users = db.users
    find = users.find({"_id": id})
    for x in find:
        json_str = json_util.dumps(x)
        data = json.loads(json_str)
        user = data["user"]
    return user
