# https://www.geeksforgeeks.org/blogs/api-security-best-practices/
# Atemptimg to use what as taught in the bootcamp in the project

import json
import os
import uuid



# url for website
url = "http://localhost:5000/hello"

#http://127.0.0.1:5000/hello?api_key=2eb95082-82ca-42e6-8eb9-d79ffc872a5c

def get_api_key():
    """Reads the api key from the api json

    Args:
        none

    Returns:
        str: The api key.
    """
    filepath = os.path.join(os.path.dirname(__file__), '..', 'security/apikey.json')
    print(f'Filepath: {filepath}')

    with open(filepath, 'r') as f:
        api_key = json.load(f)['apikey']
        print(f'api_key: {api_key}')
        return api_key

api_key = get_api_key()


#generate random api key
def generate_api_key():
    """Generates a random API key using UUID4.

    Args:
        none

    Returns:
        str: A randomly generated API key.
    """
    return str(uuid.uuid4())


# make a random UUID and convert to 32bit hex
# apikey = uuid.uuid4().hex
def create_api_key_file(apikey):
    """Creates and overwrites JSON file containing the API key.

    Args:
        apikey (str): The API key to be saved in the JSON file.

    Returns:
        text file (json): A text file with the JSON in it.
    """
    data_to_write = {'apikey': apikey}
    filepath = os.path.join(os.path.dirname(__file__), 'apikey.json')
    with open(filepath, 'w') as outfile:
        json.dump(data_to_write, outfile)


# stops from running if function is ran from other process
if __name__ == "__main__":
    get_api_key()
    api_key = generate_api_key()
    print(api_key)
    create_api_key_file(api_key)


#print(f"Authenticated link: {url}?api_key={api_key}")
