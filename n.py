from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'cinema_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinema.db'

db = SQLAlchemy(app)

# ================= MODELS =================

class Movie(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    movie_name = db.Column(
        db.String(200),
        nullable=False
    )

    genre = db.Column(
        db.String(100),
        nullable=False
    )

    ticket_price = db.Column(
        db.Integer,
        nullable=False
    )

    seats = db.Column(
        db.Integer,
        default=50
    )

    bookings = db.relationship(
        'Booking',
        backref='movie',
        lazy=True
    )

class Booking(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(
        db.String(200),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    total_price = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    movie_id = db.Column(
        db.Integer,
        db.ForeignKey('movie.id'),
        nullable=False
    )

# ================= ROUTES =================

@app.route('/')
def home():

    movies = Movie.query.all()

    return render_template(
        'movies.html',
        movies=movies
    )

@app.route('/add-movie', methods=['GET', 'POST'])
def add_movie():

    if request.method == 'POST':

        movie_name = request.form['movie_name']
        genre = request.form['genre']
        ticket_price = request.form['ticket_price']
        seats = request.form['seats']

        movie = Movie(
            movie_name=movie_name,
            genre=genre,
            ticket_price=ticket_price,
            seats=seats
        )

        db.session.add(movie)
        db.session.commit()

        return redirect('/')

    return render_template('add_movie.html')

@app.route('/book/<int:id>', methods=['GET', 'POST'])
def book_ticket(id):

    movie = Movie.query.get_or_404(id)

    if request.method == 'POST':

        customer_name = request.form['customer_name']
        quantity = int(request.form['quantity'])

        if quantity <= movie.seats:

            total_price = quantity * movie.ticket_price

            booking = Booking(
                customer_name=customer_name,
                quantity=quantity,
                total_price=total_price,
                movie_id=movie.id
            )

            movie.seats -= quantity

            db.session.add(booking)
            db.session.commit()

            flash("Ticket Booked")

            return redirect('/')

        flash("Not enough seats")

    return render_template(
        'book_ticket.html',
        movie=movie
    )

# ================= MAIN =================

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)
