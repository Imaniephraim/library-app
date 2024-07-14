from app import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    published_date = db.Column(db.Date)
    ISBN = db.Column(db.String(20), unique=True)
    availability = db.Column(db.Integer, default=1)