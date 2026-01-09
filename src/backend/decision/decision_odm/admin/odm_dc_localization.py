import os
import requests
from requests.auth import HTTPBasicAuth


def call_request2(base_url: str, username: str, password: str, method: str, endpoint: str, **kwargs):
    """
    Makes an HTTP request with basic authentication.

    Args:
        base_url (str): The base URL of the API.
        username (str): Username for authentication.
        password (str): Password for authentication.
        method (str): HTTP method (e.g., 'GET', 'POST').
        endpoint (str): API endpoint to be appended to the base URL.
        **kwargs: Additional arguments for the request, such as headers or data.

    Returns:
        Response: The HTTP response object.
    """
    auth = HTTPBasicAuth(username, password)
    url = f"{base_url}{endpoint.strip('/')}"  # Ensure no duplicate slashes in the URL
    try:
        response = requests.request(method.upper(), url, auth=auth, **kwargs)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
        print(f"Request to {endpoint} successful: {response.status_code}")
        return response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
    except requests.exceptions.RequestException as e:
        print(f"Request to {endpoint} failed: {e}")
        return None


def call_request(base_url: str, username: str, password: str, method: str, endpoint: str, **kwargs):
    auth = HTTPBasicAuth(username, password)
    url = f"{base_url}{endpoint}"
    response = requests.request(method, url, auth=auth, **kwargs)
    if response.status_code == 200:
        print(endpoint, response)
    else:
        try:
            response.raise_for_status()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    username = os.getenv("ODM_ADMIN_USERNAME")
    password = os.getenv("ODM_ADMIN_PASSWORD")
    if not username or not password:
        print("Missing ODM credentials. Set ODM_ADMIN_USERNAME and ODM_ADMIN_PASSWORD.")
    else:
        call_request(
            base_url='http://localhost:9060/decisioncenter-api',
            username=username,
            password=password,
            method='PUT',
            endpoint='/v1/DBAdmin/persistencelocale',
            params={'persistenceLocale': "fr_FR"})
