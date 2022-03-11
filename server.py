from importlib.resources import path
from flask import Flask
from flask import request, redirect
import flask
import json
import os

from utils.NeteaseCloudMusic import NeteaseDownload
from utils.ClearCache import Clear

if not os.path.exists('./cache'):   # Cache dictionary for storaging files
    os.system('mkdir ./cache')

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def Home():
    return redirect('https://ninym.top', code=301)


@app.route('/<query>', methods=['GET', "POST"])
def parser(query):
    paths = ['song', 'clear']  # All requests paths
    path = query.split('/')
    parameter = path[0]
    Error404 = {
        'code': 404,
        'msg': 'Invalid path {}'.format(parameter)
    }
    if parameter not in paths:   # When the path not exists, this will return
        return json.dumps(Error404)
    if parameter == 'song':
        id = request.args.get('id')
        ContentType = request.args.get('type')
        return NeteaseHandler(id, ContentType)
    if parameter == 'clear':
        msg = Clear()
        return msg


@app.errorhandler(404)  # 404 Handler
def not_found(e):
    print('404: ' + request.base_url)
    Error404 = {
        'code': 404,
        'msg': 'Error with information: '.format(e)
    }
    return json.dumps(Error404)


def NeteaseHandler(id, ContentType):
    if ContentType != 'attachment' and ContentType != 'json':
        ContentType = 'attachment'
    if ContentType == 'attachment':
        file, song, author = NeteaseDownload(id, ContentType)
        if file:
            return flask.send_from_directory('./song/AppData/', file, as_attachment=False, download_name='{} - {}.mp3'.format(author, song))
        else:
            if song == 404 and author == 404:
                return {'code': -1, 'msg': 'Cannot fetch resource.'}
            elif song == 'Not Found' and author == 'Not Found':
                return {'code': -2, 'msg': 'It seems that id {} is not a valid song id.'.format(id)}
    else:
        Info = NeteaseDownload(id, ContentType)
        return Info


app.run(host='0.0.0.0', port=8080, debug=True)
