
# imports
import random
import string

import os
from dotenv import load_dotenv

from flask import Flask, request, url_for, session, redirect
from functions import create_playlist, get_token


load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = "".join(random.choices(string.ascii_letters, k=16))

code = None

# --------- APP STUFF ---------
app = Flask(__name__)
app.debug = True

app.secret_key = STATE
app.config["SESSION_COOKIE_NAME"] = "Playlist Splitter"


@app.route('/')
def authenticate():

    url = 'https://accounts.spotify.com/authorize'
    url += '?response_type=code'
    url += '&client_id=' + CLIENT_ID
    url += '&scope=' + SCOPE
    url += '&redirect_uri=' + url_for(REDIRECT_URI, _external=True)
    url += '&state=' + STATE
    
    return redirect(url)


@app.route('/' + REDIRECT_URI)
def redirected():
    session.clear()
    code = request.args.get("code")
    token_info = get_token(code)
    session["token_info"] = token_info
    create_playlist()
    return "Playlist created!"