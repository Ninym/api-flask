import re
from flask import Flask, send_from_directory
from flask import request, redirect, abort, Response
from flask_analytics import Analytics
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
Analytics(app)
BaiduAnalytics = 'https://hm.baidu.com/hm.js?03bd337fcd1aa8a1b2f78d23aa552ca5'
app.config['ANALYTICS']['GOOGLE_CLASSIC_ANALYTICS']['ACCOUNT'] = 'G-ML53SEC0CG'     # Google Analytics by Flask_Analytics
app.config['ANALYTICS']['GOOGLE_UNIVERSAL_ANALYTICS']['ACCOUNT'] = 'G-ML53SEC0CG'   # Google Universal Analytics by Flask_Analytics

@app.route('/', methods=['GET'])
def Home():     # No valid path, return to the doc
    Analytics(request)
    return redirect('https://ninym.top', code=301)  


@app.route('/favicon.ico')
def favicon():  # Return favicon
    Analytics(request)
    return send_from_directory('./assets/', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/<query>', methods=['GET']) # First path handler
def parser(query):
    Analytics(request)
    paths = ['song', 'clear', 'url']  # All requests paths
    path = query.split('/')
    parameter = path[0]
    if parameter not in paths:   # When the path not exists, this will return 404
        abort(404)
    if parameter == 'song':
        id = request.args.get('id')
        ContentType = request.args.get('type')
        return NeteaseHandler(id, ContentType)
    # if parameter == 'url':
    #     operation = request.arg.get('opeation')
    #     key = request.arg.get('key')
    #     times = request.arg.get('times')
    #     return UrlParser(operation, key, times)
    if parameter == 'clear':
        msg = Clear()
        return msg

@app.route('/cache/<file>', methods=['GET'])    # Cache Handler
def cacheHandler(file):
    Analytics(request)
    return flask.send_from_directory('./cache/', file, as_attachment=False, download_name=file)


@app.route('/gh/<operation>', methods=['GET'])   # Github Handler
def ghHandler(operation):
    Analytics(request)
    author = request.args.get('author')
    repo = request.args.get('repo')
    ContentType = request.args.get('type')
    if ContentType != 'pic' and ContentType != 'json':
        ContentType = 'pic'
    return ghParser(operation, author, repo, ContentType)

@app.route('/PrivateDownloader/<operation>')
def pdHandler(operation):
    Analytics(request)
    pass

@app.errorhandler(404)  # 404 Handler
def not_found():
    Analytics(request)

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
    print('{:=^80}'.format('New request started'))
    print(request.headers)
    print('{:=^80}'.format('New request ended'))
    header = request.headers
    r.get(BaiduAnalytics, headers=header)


if __name__ == '__main__':  # Launcher
    app.run(host='0.0.0.0', port=8080, debug=True)  # If debug is set to True, every time when the file is saved the program will reload
