from flask import Flask, json, request
from flask_restful import Api, Resource, abort
import os

app = Flask(__name__)
api = Api(app)

def get_api_key():
    filepath = os.path.join(os.path.dirname(__file__), '..', 'security/apikey.json')
    print(f'Filepath: {filepath}')
    f = open(filepath, 'r')
    api_key = json.load(f)['apikey']
    print(f'API Key: {api_key}')
    f.close()
    return api_key

api_key = get_api_key()

#http://127.0.0.1:5000/
class NotAllowed(Resource):
    def get(self):
        abort(403)

#http://127.0.0.1:5000/hello
#http://127.0.0.1:5000/hello?api_key=2eb95082-82ca-42e6-8eb9-d79ffc872a5c
class HelloWorld(Resource):
    def get(self):
        key = request.headers.get('X-API-KEY') or request.args.get('api_key')
        if key == api_key:
            return {'hello': 'world'}
        else:
            abort(403)


api.add_resource(NotAllowed, '/')
api.add_resource(HelloWorld, '/hello')


if __name__ == "__main__":
    app.run(debug=True)