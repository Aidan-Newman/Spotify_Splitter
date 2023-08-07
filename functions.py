import base64
import json
import time
import datetime
from requests import post
from flask import url_for, session, redirect

import os
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = "playlist-modify-public playlist-modify-private"


def create_playlist():

    session["token_info"], authorized = check_token()

    if not authorized:
        redirect('/')

    user_id = "ob+72"
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        "Authorization": "Bearer " + session.get("token_info").get("access_token"),
        "Content-Type": "application/json"
    }
    # data = '{"name": "Spotify Splitter Playlist", ' \
    #        '"description":"Playlist Created by Playlist Splitter!", ' \
    #        '"public": false, ' \
    #        '"collaborative": false}'
    data = {
        "name": "Spotify Splitter Playlist",
        "description": "Created at: " + str(datetime.datetime.now()),
        "public": False,
        "collaborative": False
    }

    result = post(url=url, headers=headers, data=json.dumps(data))
    json_result = json.loads(result.content)
    return json_result
# ------- APP STUFF OVER -------


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


def refresh_token(refresh_token):
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


def check_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # if there's no token return ({}, False)
    if not session.get("token_info", False):
        token_valid = False
        return token_info, token_valid
    
    # check if token has expired
    current_time = int(time.time())
    token_expired = session.get("token_info").get("expires_at") - current_time < 60

    # refresh token if it's expired
    if (token_expired):
        token_info = refresh_token(session.get("token_info").get("refresh_token"))

    token_valid = True
    return token_info, token_valid