# app/routes.py
from app import app, db
from flask import Flask, request, jsonify, abort
from urllib.parse import unquote
from app.models import Book, Member, Transaction
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.schemas import BookSchema, MemberSchema
from django.core.exceptions import ValidationError
from flask_restx import Api, Resource, fields

# CRUD Opertations for Books
# Creating a new book entry
@app.route('/books', methods=['POST'])
def create_book():
    data = request.json
    new_book = Book(title=data['title'], author=data['author'], published_date=data['published_date'],ISBN=data['ISBN'], availability=data['availability'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'New book created!', 'book_id': new_book.id}), 201

# RETRIEVE details of a specific book
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        abort(404)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'published_date': str(book.published_date),
        'ISBN': book.ISBN,
        'availability': book.availability
    })
    
# UPDATE a book entry
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        abort(404)
    
    data = request.json
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.published_date = data.get('published_date', book.published_date)
    book.ISBN = data.get('ISBN', book.ISBN)
    book.availability = data.get('availability', book.availability)
    
    db.session.commit()
    return jsonify({'message': 'Book updated!', 'book_id': book.id})

# DELETE a book entry
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        abort(404)
        
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted!', 'book_id': book_id})


# Endpoints for members

# ADD a new member
@app.route('/member', methods=['POST'])
def add_member():
    data = request.json
    new_member = Member(name=data['name'], email=data['email'], membership_date=data['membership_date'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'New member added!', 'member_id': new_member.id}), 201


# RETRIEVE member details
@app.route('/member/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = Member.query.get(member_id)
    if not member:
        abort(404)
    return jsonify({
        'id': member.id,
        'name': member.name,
        'email': member.email,
        'membership_date': str(member.membership_date)
    })
    
# UPDATE member information
@app.route('/member/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    member = Member.query.get(member_id)
    if not member:
        abort(404)
    
    data = request.json
    member.name = data.get('name', member.name)
    member.email = data.get('email', member.email)
    member.membership_date = data.get('membership_date', member.membership_date)
    
    db.session.commit()
    return jsonify({'message': 'Member information updated!', 'member_id': member.id})

# DELETE a member
@app.route('/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = Member.query.get(member_id)
    if not member:
        abort(404)
    
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted!', 'member_id': member_id})

# Endpoints for transactions
# BORROW a book
@app.route('/transaction/borrow', methods=['POST'])
def borrow_book():
    data = request.json
    book_id = data.get('book_id')
    member_id = data.get('member_id')
    
    book = Book.query.get(book_id)
    if not book:
        abort(404, description='Book not found!')
    
    member = Member.query.get(member_id)
    if not member:
        abort(404, description='Member not found!')
    
    if book.availability == 0:
        return jsonify({'message': 'Book not available for borrowing!'}), 400
    
    new_transaction = Transaction(book_id=book_id, member_id=member_id, borrow_date=datetime.now())
    db.session.add(new_transaction)
    book.availability = 0  # Update availability to indicate book is borrowed
    db.session.commit()
    
    return jsonify({'message': 'Book borrowed successfully!', 'transaction_id': new_transaction.id}), 201

# RETURN a book
@app.route('/transaction/return', methods=['POST'])
def return_book():
    data = request.json
    transaction_id = data.get('transaction_id')
    
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        abort(404, description='Transaction not found!')
    
    if transaction.return_date:
        return jsonify({'message': 'Book has already been returned!'}), 400
    
    transaction.return_date = datetime.now()
    book = Book.query.get(transaction.book_id)
    book.availability = 1  # Update availability to indicate book is returned
    db.session.commit()
    
    return jsonify({'message': 'Book returned successfully!'})

# VIEW transaction history of a member
@app.route('/transaction/member/<int:member_id>', methods=['GET'])
def view_transaction_history(member_id):
    member = Member.query.get(member_id)
    if not member:
        abort(404, description='Member not found!')
    
    transactions = Transaction.query.filter_by(member_id=member_id).all()
    
    transaction_history = []
    for transaction in transactions:
        transaction_history.append({
            'id': transaction.id,
            'book_id': transaction.book_id,
            'borrow_date': str(transaction.borrow_date),
            'return_date': str(transaction.return_date) if transaction.return_date else None
        })
    
    return jsonify({'member_id': member_id, 'transaction_history': transaction_history})

# Error Handling
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': 'Resource not found'}), 404

@app.errorhandler(SQLAlchemyError)
def database_error(error):
    db.session.rollback()
    return jsonify({'error': 'Database Error', 'message': str(error)}), 500

# Input Data Validation
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

book_schema = BookSchema()
member_schema = MemberSchema()

@app.route('/books', methods=['POST'])
def create_book():
    try:
        data = request.json
        errors = book_schema.validate(data)
        if errors:
            return jsonify({'error': 'Validation Error', 'message': errors}), 400
        
        new_book = Book(title=data['title'], author=data['author'], 
                        published_date=data.get('published_date'), 
                        isbn=data['isbn'], availability=data.get('availability', True))
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Book created successfully', 'id': new_book.id}), 201
    
    except ValidationError as e:
        return jsonify({'error': 'Validation Error', 'message': str(e)}), 400
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database Error', 'message': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)

# Documentation of endpoints
api = Api()

# Define namespaces
books_ns = api.namespace('books', description='Operations related to books')
members_ns = api.namespace('members', description='Operations related to members')
transactions_ns = api.namespace('transactions', description='Operations related to transactions')

# Model schemas
book_model = api.model('Book', {
    'title': fields.String(required=True, description='Title of the book'),
    'author': fields.String(required=True, description='Author of the book'),
    'published_date': fields.Date(description='Published date of the book'),
    'isbn': fields.String(description='ISBN of the book'),
    'availability': fields.Boolean(description='Availability status of the book')
})

# Books CRUD operations
@books_ns.route('/')
class BookList(Resource):
    @books_ns.expect(book_model)
    def post(self):
        """Create a new book"""
        data = api.payload
        @app.route('/books', methods=['POST'])
        def create_book():
            data = request.json
        new_book = Book(title=data['title'], author=data['author'], published_date=data['published_date'],ISBN=data['ISBN'], availability=data['availability'])
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'New book created!', 'book_id': new_book.id}), 201
    
    @books_ns.expect(book_model)
    def put(self, book_id):
        """Update a book"""
        data = api.payload
        
        @app.route('/books/<int:book_id>', methods=['PUT'])
        def update_book(book_id):
            book = Book.query.get(book_id)
        if not book:
            abort(404)
    
        data = request.json
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.published_date = data.get('published_date', book.published_date)
        book.ISBN = data.get('ISBN', book.ISBN)
        book.availability = data.get('availability', book.availability)
    
        db.session.commit()
        return jsonify({'message': 'Book updated!', 'book_id': book.id})
    
    def delete(self, book_id):
        """Delete a book"""
        @app.route('/books/<int:book_id>', methods=['DELETE'])
        def delete_book(book_id):
            book = Book.query.get(book_id)
        if not book:
            abort(404)
            
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted!', 'book_id': book_id})