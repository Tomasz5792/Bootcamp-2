import json
import os

# url for website
url = "http://localhost:5000/hello"

#http://127.0.0.1:5000/hello?api_key=2eb95082-82ca-42e6-8eb9-d79ffc872a5c

def get_api_key():
    filepath = os.path.join(os.path.dirname(__file__), '..', 'security/apikey.json')
    print(f'Filepath: {filepath}')
    f = open(filepath, 'r')
    api_key = json.load(f)['apikey']
    print(f'API Key: {api_key}')
    f.close()
    return api_key

api_key = get_api_key()

print(f"Authenticated link: {url}?api_key={api_key}")

print("here")
