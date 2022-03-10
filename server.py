from flask import Flask
from flask import request, redirect
import flask
import json
import os

from utils.NeteaseCloudMusic import NeteaseDownload
from utils.ClearCache import Clear

if not os.path.exists('./song/AppData'):
    os.system('mkdir ./song/AppData')

Error404 = {
    'code': 404,
    'msg': 'Invalid path'
}

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def Home():
    return redirect('https://ninym.top', code=301)


@app.route('/<query>', methods=['GET', "POST"])
def parser(query):
    paths = ['song','clear']  # All requests paths
    path = query.split('/')
    parameter = path[0]
    if parameter not in paths:   # When the path not exists, this will return
        return json.dumps(Error404)
    if parameter == 'song':
        id = request.args.get('id')
        file, song, author = NeteaseDownload(id)
        if file:
            return flask.send_from_directory('./song/AppData/', file, as_attachment=False, download_name='{} - {}.mp3'.format(author, song))
    if parameter == 'clear':
        msg = Clear()
        return msg

@app.errorhandler(404)
def not_found(e):
    return json.dumps(Error404)


app.run(host='0.0.0.0', port=8080, debug=True)
