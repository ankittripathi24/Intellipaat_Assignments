from flask import ( Flask, render_template, 
                    request, flash, session, redirect, url_for)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import psycopg2


# -------------------------------------------------------------------------------------------------
app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://postgres:postgrespw@localhost:49153"
# db = SQLAlchemy(app)
connection = psycopg2.connect("postgres://postgres:postgrespw@localhost:49153/postgres")

app.config['SECRET_KEY'] = 'mysecretkey'

CREATE_MATRIX_TABLE = (
    "CREATE TABLE IF NOT EXISTS matrix (id SERIAL PRIMARY KEY, breed TEXT, \
    mood TEXT, food_choice TEXT);"
)

INSERT_MATRIX_RETURN_ID = "INSERT INTO matrix (breed, mood, food_choice) VALUES (%s, %s, %s) RETURNING id;"

# -------------------------------------------------------------------------------------------------

class InfoForm(FlaskForm):
    breed = StringField("What Breed man!", validators=[DataRequired()])
    mood = RadioField("Please choose your mood:", choices=[('mood_one', 'Happy'),('mood_two', 'Excited')])
    food_choice = SelectField(u"Pick your fav food:",
                            choices=[('chi', 'Chicken'), ('fi', 'Fish')])
    submit = SubmitField("SUBMIT")


# -------------------------------------------------------------------------------------------------

@app.route('/', methods=['GET','POST'])
def index():
    breed = False
    form = InfoForm()

    if form.validate_on_submit():
        session['breed'] = form.breed.data
        session['mood'] = form.mood.data
        session['food_choice'] = form.food_choice.data

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_MATRIX_TABLE)
                cursor.execute(INSERT_MATRIX_RETURN_ID, (session['breed'], session['mood'], session['food_choice']))

                room_id = cursor.fetchone()[0]
                print("ID IS: ", room_id)
                
        flash(f"BREED YOU JUST ENTERED IS --> {session['breed']}", breed)
        # form.breed.data = ''
        return redirect(url_for('index'))

    return render_template("index.html", form=form)


# -------------------------------------------------------------------------------------------------

if __name__== '__main__':
    # app.run(port=5000, host="0.0.0.0")
    app.run(debug=True)