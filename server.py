from importlib.resources import path
import re
from flask import Flask, send_from_directory
from flask import request, redirect
import flask
import json
import os
import requests as r

from utils.NeteaseCloudMusic import NeteaseDownload
from utils.ClearCache import Clear
# from utils.UrlJump import UrlParser
from utils.Github import ghParser

if not os.path.exists('./cache'):   # Cache dictionary for storaging files
    os.system('mkdir ./cache')

app = Flask(__name__)
BaiduAnalytics = 'https://hm.baidu.com/hm.js?03bd337fcd1aa8a1b2f78d23aa552ca5'


@app.route('/', methods=['GET', 'POST'])
def Home():
    Analytics(request)
    return redirect('https://ninym.top', code=301)


@app.route('/favicon.ico')
def favicon():  # Return favicon
    return send_from_directory('./assets/', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/<query>', methods=['GET', "POST"])
def parser(query):
    Analytics(request)
    paths = ['song', 'clear', 'url', 'gh', 'cache']  # All requests paths
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
    if parameter == 'cache':
        return open('./cache/{}'.foramt(parameter[1]),'rb')
    # if parameter == 'url':
    #     operation = request.arg.get('opeation')
    #     key = request.arg.get('key')
    #     times = request.arg.get('times')
    #     return UrlParser(operation, key, times)
    if parameter == 'clear':
        msg = Clear()
        return msg

@app.route('/gh/<operation>', methods=['GET','POST'])
def ghHandler(operation):
    author = request.args.get('author')
    repo = request.args.get('repo')
    ContentType = request.args.get('type')
    if ContentType != 'pic' and ContentType != 'json':
        ContentType = 'pic'
    print(operation,author,repo,ContentType)
    return ghParser(operation, author, repo, ContentType)

@app.errorhandler(404)  # 404 Handler
def not_found():
    Error404 = {
        'code': 404,
        'msg': 'Not found while accessing '.format(request.url)
    }
    return json.dumps(Error404)

@app.errorhandler(500)  # 404 Handler
def not_found():
    Error500 = {
        'code': 500,
        'msg': 'Internal Server Error'
    }
    return json.dumps(Error500)

def NeteaseHandler(id, ContentType):
    if ContentType != 'attachment' and ContentType != 'json':
        ContentType = 'attachment'
    if ContentType == 'attachment':
        file, song, author = NeteaseDownload(id, ContentType)
        if file:
            return flask.send_from_directory('./cache/', file, as_attachment=False, download_name='{} - {}.mp3'.format(author, song))
        else:
            if song == 404 and author == 404:
                return {'code': -1, 'msg': 'Cannot fetch resource.'}
            elif song == 'Not Found' and author == 'Not Found':
                return {'code': -2, 'msg': 'It seems that id {} is not a valid song id.'.format(id)}
    else:
        Info = NeteaseDownload(id, ContentType)
        return Info


def Analytics(request):
    print(request.headers)
    header = request.headers
    r.get(BaiduAnalytics, headers=header)


if __name__ == '__main__':  # Main function
    app.run(host='0.0.0.0', port=8080, debug=True)
