import requests


def open_dict(address, page=""):
    url = address.rstrip("/")
    if page:
        url = f"{url}/{requests.utils.quote(str(page).strip().strip('/'), safe='')}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    dictionary_required = response.json()

    return dictionary_required
