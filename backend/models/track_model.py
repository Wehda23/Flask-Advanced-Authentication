from .base_model import db


class TrackModel(db.Model):
    __tablename__ = "tracks_model"

    token = db.Column(db.String(2056), primary_key=True)
    instance_id = db.Column(db.String(2056), nullable=False)
    token_type = db.Column(db.String(128), nullable=False)
