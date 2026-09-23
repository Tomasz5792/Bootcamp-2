# https://www.geeksforgeeks.org/blogs/api-security-best-practices/
# Atemptimg to use what as taught in the bootcamp in the project

import json
import os
import uuid
from werkzeug.security import generate_password_hash

# url for website
#url = "http://localhost:5000/hello" # I dont think this is needed anymore

# JSON file path
filepath = os.path.join(os.path.dirname(__file__), 'apikey.json')
#filepath = os.path.join(os.path.dirname(__file__), '..', 'security/apikey.json') old filepath
print(f'Filepath: {filepath}')


#generate random api key
def create_api_key():
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
    with open(filepath, 'w') as outfile:
        json.dump(data_to_write, outfile)


def get_api_key():
    """Reads the api key from the api json

    Args:
        none

    Returns:
        str: The api key.
    """
    with open(filepath, 'r') as f:
        api_key = json.load(f)['apikey']
        return api_key
    

def create_hashed_password(password):
    """Takes a password and hashes it for storage

    Args:
        password (str): individuals password

    Returns:
        str: The password hashed
    """
    #hashed_password = generate_password_hash(password)
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    return hashed_password


# stops from running if function is ran from other process
if __name__ == "__main__":
    api_key = create_api_key()
    print(f'generated api_key: {api_key}')
    hashed_password = create_hashed_password("password")
    print(f'generated hashed_password: {hashed_password}')
    #create_api_key_file(api_key)
    #get_api_key()



#print(f"Authenticated link: {url}?api_key={api_key}")
