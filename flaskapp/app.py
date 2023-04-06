from flask import ( Flask, render_template, 
                    request, flash, session, redirect, url_for)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, SelectField
from wtforms.validators import DataRequired
import re

from flask_sqlalchemy import SQLAlchemy
import psycopg2
import urllib.parse as up
import os


# -------------------------------------------------------------------------------------------------

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://postgres:postgrespw@localhost:49153"
# db = SQLAlchemy(app)

## This is Postgresql URL for postgres hosted on Local Docker
# connection = psycopg2.connect("postgres://postgres:postgrespw@localhost:49153/postgres")


# To Connect to AVIN POSTGRES Uncomment this
# connection = psycopg2.connect('postgres://avnadmin:AVNS_ZimXsDMMy8ate5HVK1c@service-ankit-project-ankit.aivencloud.com:24181/defaultdb?sslmode=require')

# To connect to ElephantSQL
# This is Postgresql URL for postgres hosted on https://api.elephantsql.com/
connection = psycopg2.connect('postgres://pmidhwez:fAANibTwAfkBWOHPWCd74SbuCepivRXB@hansken.db.elephantsql.com/pmidhwez')

app.config['SECRET_KEY'] = 'mysecretkey'

CREATE_MATRIX_TABLE = (
    "CREATE TABLE IF NOT EXISTS matrix (SIX_PAGER TEXT PRIMARY KEY, \
    EPIC TEXT UNIQUE , LINKED_EPIC TEXT, FIX_VERSION TEXT UNIQUE, STORY TEXT, OTHERS TEXT);"
)

INSERT_MATRIX_RETURN_ID = "INSERT INTO matrix (SIX_PAGER, EPIC, LINKED_EPIC, FIX_VERSION, STORY, OTHERS) VALUES (%s, %s, %s, %s, %s, %s) RETURNING SIX_PAGER;"

GET_ALL_MATRIX = "SELECT * FROM matrix;"


# -------------------------------------------------------------------------------------------------


class InfoForm(FlaskForm):
    EPIC = StringField("ENTER EPIC ID THAT IS LINKED TO 6PAGER!", validators=[DataRequired()])
    LINKED_EPIC = StringField("ENTER LINKED_EPIC ID!", validators=[DataRequired()])
    SIX_PAGER = StringField("ENTER UNIQUE SIX_PAGER ID!", validators=[DataRequired()])
    STORY = StringField("ENTER COMMA SEPERATED STORY IDs!", validators=[DataRequired()])
    FIX_VERSION = StringField("ENTER UNIQUE FIX_VERSION ID!", validators=[DataRequired()])
    OTHERS = StringField("EXTRA INFORMATION!")
    submit = SubmitField("SUBMIT")

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/getallMatrix')
def getallMatrix():
    var_to_be_inserted = "Ankit Says :- "
    LIST_RECORDS = []
    INDIVIDUAL_RECORD = {}
    try:
        with connection:
            with connection.cursor() as cursor:
                
                cursor.execute(GET_ALL_MATRIX)

                RECORDS = cursor.fetchall()
                
                for row in RECORDS:
                    INDIVIDUAL_RECORD["SIX_PAGER"] =  row[0],
                    INDIVIDUAL_RECORD["EPIC"] = row[1]
                    INDIVIDUAL_RECORD["LINKED_EPIC"]  = row[2]
                    INDIVIDUAL_RECORD["FIX_VERSION"] =  row[3],
                    INDIVIDUAL_RECORD["STORY"] = row[4]
                    INDIVIDUAL_RECORD["OTHERS"]  = row[5]

                    print("RECORD IS: ", INDIVIDUAL_RECORD)
                    dict_copy = dict(INDIVIDUAL_RECORD)  # 👈️ create copy

                    LIST_RECORDS.append(dict_copy)
                    print(LIST_RECORDS)
        
    except:
        flash(f"NO DATA FOUND IN THE TABLE, PLEASE INSERT SOME VALUES ")
        print(f"NO DATA FOUND IN THE TABLE, PLEASE INSERT SOME VALUES ")
        cursor.close()
        connection.close()
    print(LIST_RECORDS)
    return render_template("getMatrix.html", var_to_be_inserted=var_to_be_inserted, LIST_RECORDS=LIST_RECORDS)

@app.route('/createMatrix', methods=['GET','POST'])
def createMatrix():
    SIX_PAGER, FIX_VERSION, STORY, LINKED_EPIC, EPIC = None, None, None, None, None
    form = InfoForm()

    if form.validate_on_submit():
        session['SIX_PAGER'] = form.SIX_PAGER.data
        stringRegex = re.compile(r'DM-')
        var = session['SIX_PAGER']
        if stringRegex.search(var) != None:
            SIX_PAGER = session['SIX_PAGER']
        
        session['EPIC'] = form.EPIC.data
        stringRegex = re.compile(r'EPIC-')
        var = session['EPIC']
        if stringRegex.search(var) != None:
            EPIC = session['EPIC']

        session['LINKED_EPIC'] = form.LINKED_EPIC.data
        stringRegex = re.compile(r'EPIC-')
        var = session['LINKED_EPIC']
        if stringRegex.search(var) != None:
            LINKED_EPIC = session['LINKED_EPIC']
        
        session['STORY'] = form.STORY.data
        stringRegex = re.compile(r'MDS-')
        var = session['STORY']
        if stringRegex.search(var) != None:
            STORY = session['STORY']
        
        session['FIX_VERSION'] = form.FIX_VERSION.data
        stringRegex = re.compile(r'FV-')
        var = session['FIX_VERSION']
        if stringRegex.search(var) != None:
            FIX_VERSION = session['FIX_VERSION']
        
        OTHERS = form.OTHERS.data
        
        if (SIX_PAGER or EPIC or FIX_VERSION or STORY or LINKED_EPIC) is None:
            flash(f"DATA YOU JUST ENTERED FAILED IN PARSING --> {SIX_PAGER, EPIC, LINKED_EPIC, FIX_VERSION, STORY}")
            # form.breed.data = ''
        else:
            try:
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute(CREATE_MATRIX_TABLE)
                        cursor.execute(INSERT_MATRIX_RETURN_ID, (SIX_PAGER, EPIC, LINKED_EPIC, FIX_VERSION, STORY, OTHERS))

                        SIX_PAGER_ID = cursor.fetchone()[0]
                        print("ID IS: ", SIX_PAGER_ID)
                flash(f"SUCCESSFULLY ENTERED --> {SIX_PAGER, EPIC, LINKED_EPIC, FIX_VERSION, STORY, OTHERS}")
            except:
                flash(f"DATA YOU JUST ENTERED FAILED IN UNIQUINESS --> {SIX_PAGER, EPIC, LINKED_EPIC, FIX_VERSION, STORY}")
                print(f"DATA YOU JUST ENTERED FAILED IN UNIQUINESS --> {SIX_PAGER, EPIC, LINKED_EPIC, FIX_VERSION, STORY}")
                cursor.close()
                connection.close() 
        return redirect(url_for('createMatrix'))

    return render_template("createMatrix.html", form=form)
    

@app.route('/thank_you')
def thank_you():
    EPIC_ID = request.args.get('EPIC_ID')
    LINKED_EPIC_ID = request.args.get('LINKED_EPIC_ID')

    return render_template("thank_you.html", LINKED_EPIC_ID=LINKED_EPIC_ID, EPIC_ID=EPIC_ID)

@app.route('/show/<MDS_ID>')
def show_MDS_ID(MDS_ID):
    return render_template("basic.html", MDS_ID=MDS_ID)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

if __name__== '__main__':
    app.run(host="0.0.0.0")
    # app.run(debug=True)
    