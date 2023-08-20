
# imports
import random
import string

import atexit

import os
from dotenv import load_dotenv
from flask import Flask, session, request, redirect, render_template, url_for

from spotify_splitter import get_token, get_user_playlists, get_playlist_items, get_track_audio_features

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
        return redirect('/testing')


@app.route('/testing', methods=['POST', 'GET'])
def testing():

    # if there's no token stored redirect to authorize
    if not session.get("token_info", False):
        return redirect('/')

    # if the submit button has been pressed and a post request has been sent
    elif request.method == 'POST':
        for playlist in get_user_playlists():
            if playlist["name"] == request.form.get("playlist"):
                highest = 0
                highest_track = None
                for item in get_playlist_items(playlist["id"]):
                    track = item["track"]
                    valence = get_track_audio_features(track["id"])["valence"]
                    # ignore = ["Kids", "Before You Go"]
                    if valence > highest:  # and track["name"] not in ignore:
                        highest = valence
                        highest_track = track["name"]
                return highest_track

        return "error"

    # prompt user for the playlist
    else:
        html_file = open("templates/testing.html", "w")

        html_body =\
            "<form method='post'>\
                <label for='playlist'>Select a playlist:</label>\
                <select id='playlist' name='playlist'>"
        for playlist in get_user_playlists():
            html_body += "<option value='" + playlist["name"] + "'>" + playlist["name"] + "</option>"
        html_body +=\
            "\
                </select>\
                <input type='submit' id='submit' value='Submit!'>\
            </form>"

        html_file.write('<!DOCTYPE html>' + html_body + '<body></body></html>')
        html_file.close()

        return render_template("testing.html")


# @app.route('/handle_submit', methods=['POST'])
# def handle_submit():
#     form_data = request.form
#     return json.dumps(form_data)


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
