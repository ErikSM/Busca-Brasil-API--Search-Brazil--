import requests
import json


def open_dict(address, page=""):
    request = requests.get(f"{address}/{page}")
    dictionary_required = json.loads(request.text)

    return dictionary_required
