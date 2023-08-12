import base64
import json
import time

import requests
from requests import post, get, delete
from flask import url_for, session

import os
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
BAD_TOKEN_CODE = 401
GOOD_RESPONSE_CODES = [200, 201, 202, 204]
REFRESH_ATTEMPTS = 1


def get_user_id():
    """
    Gets the current session's authorized user's id.
    :return: user_id
    """
    result = make_request(
        "get",
        "https://api.spotify.com/v1/me",
        {},
    )
    return result["id"]


def create_playlist(name, description, public, collaborative):
    """
    Creates a playlist for the specified user (by user id).
    :return: result
    """
    user_id = get_user_id()
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        # "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
    data = {
        "name": name,
        "description": description,
        "public": public,
        "collaborative": collaborative
    }
    data = json.dumps(data)
    result = make_request("post", url, headers, data)
    return json.loads(result)


def get_user_playlists():
    """
    Gets the current authorized user's playlists.
    :return: List of playlist items.
    """
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {}
    result = make_request("get", url, headers)
    return result["items"]


def make_request(method=None, url=None, headers=None, data=None):
    """
    Makes a request with the Python requests library. If the returned status code is the
    BAD_TOKEN_CODE then an attempt is made to refresh the token until the MAX_REFRESH_ATTEMPTS is
    reached. If the returned status code is not a good response code an exception is thrown. If the
    returned status code is a good response code the response is returned in json.
    :return: result
    """
    bad_token = True
    attempts = 0
    while bad_token and attempts <= REFRESH_ATTEMPTS:

        result: requests.Response
        headers["Authorization"] = "Bearer " + session.get("token_info").get("access_token")
        match method:
            case "post":
                result = post(url=url, headers=headers, data=data)
            case "get":
                result = get(url=url, headers=headers, data=data)
            case "delete":
                result = delete(url=url, headers=headers, data=data)
            case _:
                raise Exception("Invalid Method")

        print(result.status_code)
        if result.status_code == BAD_TOKEN_CODE:
            update_token()
            attempts += 1
        elif result.status_code not in GOOD_RESPONSE_CODES:
            raise Exception("Request error " + str(result.status_code))
        else:
            print("good code")
            return json.loads(result.content)
    raise Exception("Refresh Attempts Surpassed")


# gap
# gap
# gap
# --------- Token Management ---------
def get_token(code):
    """
    Requests a token from Spotify after OAuth has been completed.
    :return: List of playlist items.
    """
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + get_encoded_header(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": url_for(REDIRECT_URI, _external=True)
    }
    result = post(url, headers=headers, data=data)
    token_info = json.loads(result.content)
    if "error" in token_info.keys():
        return None, token_info["error"], token_info["error_description"]
    token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
    return token_info, None, None


def get_refreshed_token(refresh_token):
    """
    Requests a refreshed token from Spotify using a provided refresh token.
    :return: token_info
    """
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + get_encoded_header()
    }
    data = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    result = post(url=url, headers=headers, data=data)
    token_info = json.loads(result.content)
    token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
    if "refresh_token" not in token_info:
        token_info["refresh_token"] = refresh_token
    return token_info


def update_token():
    """
    Checks if a token has been acquired; if not it redirects to authorize. Then checks if the token is expired. If it
    is, it requests a refreshed token and updates the session's token_info.
    """
    token_info = session.get("token_info", {})
    #
    # # if there's no token return ({}, False)
    # if not session.get("token_info", False):
    #     return None

    # check if token has expired
    current_time = int(time.time())
    token_expired = session.get("token_info").get("expires_at") - current_time < 60

    # refresh token if it's expired
    if token_expired:
        token_info = get_refreshed_token(session.get("token_info").get("refresh_token"))

    session["token_info"] = token_info
    return token_info["access_token"]


def get_encoded_header():
    """
    Creates the encoded header with the client_id and the client_secret.
    :return: encoded_header
    """
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    return auth_base64
