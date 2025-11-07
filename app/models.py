from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    location = db.Column(db.String(255))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
