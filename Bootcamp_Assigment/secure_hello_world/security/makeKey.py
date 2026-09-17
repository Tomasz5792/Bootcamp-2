import uuid
import json
import os

#make random api key

def generate_api_key():
    """Generates a random API key using UUID4.

    Returns:
        str: A randomly generated API key.
    """
    return str(uuid.uuid4())

# make a random UUID and convert to 32bit hex
#apikey = uuid.uuid4().hex
def create_api_key_file(apikey):
    """Creates a JSON file containing the API key.

    Args:
        apikey (str): The API key to be saved in the JSON file.
    """
    data_to_write = {'apikey': apikey}
    filepath = os.path.join(os.path.dirname(__file__), 'apikey.json')
    with open(filepath, 'w') as outfile:
        json.dump(data_to_write, outfile)


if __name__ == "__main__":
    api_key = generate_api_key()
    print(api_key)
    create_api_key_file(api_key)