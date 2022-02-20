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

    Source: https://getpocket.com/developer/docs/authentication
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

    Source: https://getpocket.com/developer/docs/authentication
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


def get_list(
    access_token: str,
    state: str = None,
    favorite: int = None,
    tag: str = None,
    content_type: str = None,
    sort: str = None,
    detail_type: str = None,
    search: str = None,
    domain: str = None,
    since: int = None,
    count: int = None,
    offset: int = None,
) -> dict:
    """
    Get Pocket List

    Source: https://getpocket.com/developer/docs/v3/retrieve

    :param access_token: (optional) Pocket access token
    :type access_token: str

    :param state: (optional) State of the item. Valid values: unread, archive, all (default: unread)
    :type state: str

    :param favorite: Favorite of the item. Valid values: 0, 1
    :type favorite: int

    :param tag: (optional) Tag of the items.
    :type tag: str

    :param content_type: (optional) Content type of the item. Valid values: article, video, image, all (default: all)
    :type content_type: str

    :param sort: (optional) Sort order of the items. Valid values: newest, oldest, title, site (default: newest)
    :type sort: str

    :param detail_type: (optional) Detail type of the item. Valid values: simple, complete (default: simple)
    :type detail_type: str

    :param search: (optional) Search query.
    :type search: str

    :param domain: (optional) Domain of the item.
    :type domain: str

    :param since: (optional) Unix timestamp of the oldest item to retrieve.
    :type since: int

    :param count: (optional) Number of items to retrieve.
    :type count: int

    :param offset: (optional) Number of items to offset the result by.
    :type offset: int

    :return: a dict with the following keys:
        - status: True if the request was successful, False otherwise
        - status_code: the HTTP status code of the response (if status is False)
        - message: the error message (if status is False)
        - data: a dict with the following keys (if status is True)
    """
    data = {
        "consumer_key": config.POCKET_CONSUMER_KEY,
        "access_token": access_token,
        "state": state,
        "favorite": favorite,
        "tag": tag,
        "contentType": content_type,
        "sort": sort,
        "detailType": detail_type,
        "search": search,
        "domain": domain,
        "since": since,
        "count": count,
        "offset": offset,
    }
    url = f"{POCKET_BASE_URL}/v3/get"
    response = requests.post(url, data=data, headers=headers)
    if response.ok:
        data = response.json()
        return {
            "status": True,
            "data": data,
        }
    return {
        "status": False,
        "status_code": response.status_code,
        "message": response.text,
    }
