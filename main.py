from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

MOVIES_DATABASE_API_KEY = 'b83cb4d88f23a2de02eeccc0317250dd'
MOVIE_SEARCH_ENDPOINT = 'https://api.themoviedb.org/3/search/movie'
MOVIE_DETAILS_END_POINT = 'https://api.themoviedb.org/3/movie/'

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies_collection2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250), nullable=False, unique=True, default='')
    year = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=False, default='')
    rating = db.Column(db.Float, nullable=False, default=0.0)
    # ranking = db.Column(db.Integer,primary_key=True, autoincrement = True)
    review = db.Column(db.Text, nullable=False, default='')
    img_url = db.Column(db.String(1000), nullable=False, default='')


db.create_all()


class EditForm(FlaskForm):
    rating = FloatField(label='Your Rating Out Of 10 e.g:7.5',
                        validators=[DataRequired(message='Please Add Your New Rating ')])
    review = StringField(label='Your Review', validators=[DataRequired(message='Please Add Your Review')])
    update = SubmitField(label='Update')


class AddForm(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired()])
    add = SubmitField(label='Add')


@app.route("/")
def home():
    movies = db.session.query(Movies).all()
    return render_template("index.html", movies=movies)


@app.route("/movie/<int:id>/update", methods=['POST', 'GET'])
def edit(id):
    edit_form = EditForm()
    movie_to_update = Movies.query.get(id)
    if edit_form.validate_on_submit():
        movie_to_update.rating = edit_form.data['rating']
        movie_to_update.review = edit_form.data['review']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=edit_form, movie=movie_to_update)


@app.route('/movie/<int:id>/delete')
def delete(id):
    movie_to_delete = Movies.query.get(id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_name = form.data['title']
        movie_search_parameters = {
            'api_key': MOVIES_DATABASE_API_KEY,
            'query': movie_name
        }
        response = requests.get(url=MOVIE_SEARCH_ENDPOINT, params=movie_search_parameters)
        movies_data = response.json()
        movies_list = movies_data['results']
        return render_template('select.html', movies=movies_list)
    return render_template('add.html', form=form)


@app.route('/movie/added/<int:id>')
def added(id):
    params = {
        'api_key': MOVIES_DATABASE_API_KEY
    }
    response = requests.get(url=MOVIE_DETAILS_END_POINT + f'{id}', params=params)
    movie_data = response.json()
    movie_to_add = Movies(
        title=movie_data['original_title'],
        year=int(movie_data['release_date'].split('-')[0]),
        description=movie_data['overview'],
        img_url=f"https://image.tmdb.org/t/p/w500{movie_data['poster_path']}",
    )
    db.session.add(movie_to_add)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
