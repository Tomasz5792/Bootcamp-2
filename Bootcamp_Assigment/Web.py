from flask import Flask
from flask_restful import Api, Resource, abort

app = Flask(__name__)
api = Api(app)

#http://127.0.0.1:5000/
class NotAllowed(Resource):
    def get(self):
        abort(403)

#http://127.0.0.1:5000/hello
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}
    
#print(HelloWorld().get())

api.add_resource(NotAllowed, '/')
api.add_resource(HelloWorld, '/hello')


if __name__ == "__main__":
    app.run(debug=True)