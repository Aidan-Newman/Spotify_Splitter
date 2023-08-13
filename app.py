
# imports
import random
import string

import atexit
import signal
import flask
# import datetime

from flask import Flask, request, redirect, render_template

import functions
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
def authorize():
    # if a token is already stored redirect to redirect uri
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
def handle_authorization():
    # if a token is already stored display error
    if session.get("token_info", False):
        return "Authentication already completed..."
    else:
        session.clear()
        code = request.args.get("code")
        token_info, token_error = get_token(code)[0:2]
        if token_error:
            return redirect('/')
        session["token_info"] = token_info
        return redirect('/get_user_playlists')


@app.route('/get_user_playlists')
def get_user_playlists():
    # if there's no token stored redirect to authorize
    if not session.get("token_info", False):
        return redirect('/')
    else:
        html_file = open("templates/testing.html", "w")

        html_body =\
            "<form action='/data' method='post'>\
                <label for='playlist'>Select a playlist:</label>\
                <select id='playlist' name='playlist'>"
        for playlist in functions.get_user_playlists():
            html_body += "<option value='" + playlist["name"] + "'>" + playlist["name"] + "</option>"
        html_body +=\
            "\
                </select>\
                <input type='submit' id='submit' value='Submit!'>\
            </form>"

        html_file.write('<!DOCTYPE html>' + html_body + '<body></body></html>')
        html_file.close()

        return render_template("testing.html")


@app.route('/data', methods=['POST'])
def data():
    form_data = request.form
    return json.dumps(form_data)


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return "Token information deleted."


def exit_flask():
    html_file = open("templates/testing.html", "w")
    html_file.write('')
    html_file.close()


atexit.register(exit_flask)
