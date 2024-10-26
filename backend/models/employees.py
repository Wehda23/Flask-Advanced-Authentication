"""
File contains employees model
"""

from .base_model import db


class Employees(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
