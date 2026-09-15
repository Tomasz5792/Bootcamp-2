#https://flask.palletsprojects.com/en/stable/quickstart/#a-minimal-application
#http://127.0.0.1:5000/

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    app.run(debug=True)