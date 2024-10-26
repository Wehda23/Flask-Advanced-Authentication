"""
File contains Managers model
"""

from .base_model import db


class Managers(db.Model):
    __tablename__ = "managers"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
