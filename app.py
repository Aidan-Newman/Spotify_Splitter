
# imports
import random
import string
# import datetime

from flask import Flask, request, redirect

from functions import *

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = os.getenv("SCOPE")
STATE = "".join(random.choices(string.ascii_letters, k=16))

# --------- APP STUFF ---------
app = Flask(__name__)
app.debug = True

app.secret_key = STATE
app.config["SESSION_COOKIE_NAME"] = "Playlist Splitter"


@app.route('/')
def authenticate():

    if session.get("token_info", False):
        return redirect("/" + REDIRECT_URI)
    else:
        url = 'https://accounts.spotify.com/authorize'
        url += '?response_type=code'
        url += '&client_id=' + CLIENT_ID
        url += '&scope=' + SCOPE
        url += '&redirect_uri=' + url_for(REDIRECT_URI, _external=True)
        url += '&state=' + STATE
        url += '&show_dialog=true'
        return redirect(url)


@app.route('/' + REDIRECT_URI)
def redirected():
    if session.get("token_info", False):
        return "Authentication already completed..."
    else:
        session.clear()
        code = request.args.get("code")
        token_info, token_error = get_token(code)[0:2]
        if token_error:
            return redirect('/')
        session["token_info"] = token_info
        return "Authenticated!"


@app.route('/new_playlist')
def new_playlist():
    create_playlist("test", "testing", False, False)
    return "Playlist created!"


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return "Token information deleted."
