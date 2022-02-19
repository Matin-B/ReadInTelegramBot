import requests

import config

POCKET_BASE_URL = config.POCKET_BASE_URL
BASE_REDIRECT_URL = config.BASE_REDIRECT_URL

headers = {
    "X-Accept": "application/json",
}


def request_auth_code(user_id: int) -> dict:
    """
    Request Pocket authorization code
    """
    url = f"{POCKET_BASE_URL}/v3/oauth/request"
    data = {
        "consumer_key": config.POCKET_CONSUMER_KEY,
        "redirect_uri": f"{BASE_REDIRECT_URL}{user_id}",
    }
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return {
            "status": True,
            "code": data["code"],
        }
    return {
        "status": False,
        "status_code": response.status_code,
        "message": response.text,
    }


def generate_auth_url(user_id: int, code: str) -> str:
    """
    Generate Pocket authorization URL
    """
    redirect_url = f"{BASE_REDIRECT_URL}{user_id}"
    return f"{POCKET_BASE_URL}/auth/authorize?"\
        f"request_token={code}&redirect_uri={redirect_url}"


def request_auth_access_token(code: str) -> dict:
    """
    Request Pocket authorization access token
    """
    url = f"{POCKET_BASE_URL}/v3/oauth/authorize"
    data = {
        "consumer_key": config.POCKET_CONSUMER_KEY,
        "code": code,
    }
    response = requests.post(url, data=data, headers=headers)
    if response.ok:
        data = response.json()
        access_token = data["access_token"]
        username = data["username"]
        return {
            "status": True,
            "access_token": access_token,
            "username": username,
        }
    return {
        "status": False,
        "status_code": response.status_code,
        "message": response.text,
    }

