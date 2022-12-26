from flask import Flask, render_template, request


# from UI.JIRAMatrixCreation import *

app = Flask(__name__)

@app.route('/')
def index():
    # strMatrixTable= get_Matrix()
    return render_template("basic_1.html")#, strMatrixTable=strMatrixTable)



if __name__== '__main__':
    app.run(debug=True)