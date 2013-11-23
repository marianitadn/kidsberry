import json

from flask import Flask, request, session, redirect, url_for

from camera_picture import CameraPicture
from camera_video import CameraVideo
from database import db_session
from models import User
from settings_local import FLASK_SECRET_KEY

DEFAULT_VIDEO_DURATION = 120

app = Flask(__name__)


@app.route('/')
def home():
    response = {'response': 'HI!'}
    return json.dumps(response)


@app.route('/sign_up', methods=['POST'])
def sign_up():
    request_data = json.loads(request.form)
    new_user = User(username=request_data['username'], email=request_data['email'])
    db_session.add(new_user)
    db_session.commit()
    response = {'response': 'Your account was successfully created'}
    return json.dumps(response)


@app.route('/login', methods=['POST'])
def login():
    request_credentials = json.loads(request.form)
    if session.get(request_credentials['username']):
        response = {'response': 'You are already logged in!'}
    else:
        session['username'] = request_credentials['username']
        response = {'response': 'Successfully logged in!',
                    'data': {'username': session['username']}}

    return json.dumps(response)


@app.route('/logout')
def logout():
    session.pop('username', None)
    response = {'response': 'Successfully logged out!'}
    return json.dumps(response)


@app.route('/create_dropbox_session', methods=['POST'])
def create_dropbox_session():
    """Assert if the given access token is the one saved for the user in the
    database, else update the access_token.
    Return a new Dropbox client session for the user.
    """
    user_access_token = get_user_dropbox_access_token
    access_token = json.loads(request.form)['access_token']

    if user_access_token != access_token:
        user.update({'dropbox_access_token': access_token})
    return get_dropbox_session(access_token)


def get_dropbox_session(access_token=None):
    """Try to connect to Dropbox. If the token is valid then return the client.
    """
    if not access_token:
        access_token = get_user_dropbox_access_token()
    try:
        dropbox = DropboxClient(access_token)
    except Exception:
        app.logger.warning("User wasn't able to authenticate to Dropbox!")
        return

    return dropbox.client


def get_user_dropbox_access_token():
    user = User.query.get(User.username == session['username'])
    return user.dropbox_access_token


@app.route('/take_picture')
def take_picture():
    """Connect to the RasberryPi and take a picture using the wrapper class.
    Upload the file to Dropbox and send the URL to the client.
    """
    camera = CameraPicture()
    filename = camera.take_picture()

    client = get_dropbox_session()
    file_url = client.upload(filename)

    response = {'response': 'OK', 'data': {'file_url': file_url}}
    return json.dumps(response)


@app.route('/take_video')
def take_video():
    """Take a video of a fixed duration, if none is given set the default to
    2 minutes, upload the video on Dropbox and return the file URL.
    """
    duration = json.loads(request.form).get('duration')
    if not duration:
        duration = DEFAULT_VIDEO_DURATION

    video = CameraVideo()
    filename = video.take_video(duration)

    client = get_dropbox_session()
    video_url = client.upload(filename)

    response = {'data': {'video_url': video_url}}


@app.route('/live_preview', methods=['POST, DELETE'])
def live_preview():
    """If the client makes a POST request start the live preview, and add the
    CameraVideo object to the session to be able to end the live preview once
    the client makes a DELETE request.
    """
    if request.method == 'POST':
        video = CameraVideo()
        session['video'] = video
        video.start_live_preview()

    elif request.method == 'DELETE':
        video = session.get('video')
        if video:
            video.end_live_preview()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.config.from_object('kidsberry_config.KidsberryConfig')
    app.run()
