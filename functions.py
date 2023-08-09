import base64
import json
import time
import datetime
from requests import post, get
from flask import url_for, session, redirect

import os
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")


def get_user_id():

    token = get_updated_token()

    url = "https://api.spotify.com/v1/me"
    headers = {
        "Authorization": "Bearer " + token,
    }
    result = get(url=url, headers=headers)
    json_result = json.loads(result.content)
    return json_result["id"]


def create_playlist():

    token = get_updated_token()

    user_id = get_user_id()
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
    data = {
        "name": "Spotify Splitter Playlist",
        "description": "Created at: " + str(datetime.datetime.now()),
        "public": False,
        "collaborative": False
    }

    result = post(url=url, headers=headers, data=json.dumps(data))
    json_result = json.loads(result.content)
    return json_result


def get_user_playlists():

    token = get_updated_token()

    url = "https://api.spotify.com/v1/me/playlists"
    headers = {
        "Authorization": "Bearer " + token,
    }
    result = get(url=url, headers=headers)
    json_result = json.loads(result.content)

    return json_result["items"]


# gap
# gap
# gap
# --------- Token Management ---------
def get_token(code):
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": url_for(REDIRECT_URI, _external=True)
    }
    result = post(url, headers=headers, data=data)
    token_info = json.loads(result.content)
    token_info["expires_at"] = int(time.time()) + token_info["expires_in"]

    return token_info


def get_refresh_token(refresh_token):
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64
    }
    data = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    result = post(
        url=url,
        headers=headers,
        data=data
    )
    token_info = json.loads(result.content)
    session["token_info"]["expires_at"] = int(time.time()) + token_info["expires_in"]
    if "refresh_token" not in token_info:
        token_info["refresh_token"] = refresh_token
    return token_info


def get_updated_token():
    token_info = session.get("token_info", {})

    # if there's no token return ({}, False)
    if not session.get("token_info", False):
        redirect('/')
        return None

    # check if token has expired
    current_time = int(time.time())
    token_expired = session.get("token_info").get("expires_at") - current_time < 60

    # refresh token if it's expired
    if token_expired:
        token_info = get_refresh_token(session.get("token_info").get("refresh_token"))

    session["token_info"] = token_info
    return token_info


# --------- Misc ---------
