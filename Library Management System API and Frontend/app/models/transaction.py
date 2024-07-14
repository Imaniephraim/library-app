from app import db

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    
    book = db.relationship('Book', backref=db.backref('transactions', lazy=True))
    member = db.relationship('Member', backref=db.backref('transactions', lazy=True))