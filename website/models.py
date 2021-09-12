from . import db
from flask_login import UserMixin

sols = db.Table('sols',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('problem_id', db.Integer, db.ForeignKey('problem.id'))
                )


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    problemsNum = db.Column(db.Integer)
    index = db.Column(db.Integer)
    listNum = db.Column(db.Integer)
    members = db.relationship('User')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    teamId = db.Column(db.Integer, db.ForeignKey('team.id'))


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(7))
    solvers = db.relationship('User', secondary=sols, backref=db.backref('solutions', lazy='dynamic'))
