import logging
from lib2to3.pgen2 import token
import re
from flask import Flask, send_from_directory, Blueprint
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
from utils.Pixiv import PixivImgDownload
from utils.Osu import MapDownloader
from utils.HexoLinkCheck import blueprint as hexo_link_check_blueprint

# Logtail Register
from logtail import LogtailHandler
handler = LogtailHandler(source_token="mquAcDGSyhpjY47S9YxLeEce")
# Logtail Register Ends

# Log Collector
logger = logging.getLogger(__name__)
logger.handlers = []
logger.setLevel(logging.INFO)
logger.addHandler(handler)
# Log Collector Ends

if not os.path.exists('./cache'):   # Cache dictionary for storaging files
    os.system('mkdir ./cache')

app = Flask(__name__)
Analytics(app)
BaiduAnalytics = 'https://hm.baidu.com/hm.js?03bd337fcd1aa8a1b2f78d23aa552ca5'
# Google Analytics by Flask_Analytics
app.config['ANALYTICS']['GOOGLE_CLASSIC_ANALYTICS']['ACCOUNT'] = 'G-ML53SEC0CG'
# Google Universal Analytics by Flask_Analytics
app.config['ANALYTICS']['GOOGLE_UNIVERSAL_ANALYTICS']['ACCOUNT'] = 'G-ML53SEC0CG'
Redis_URI = os.environ.get('REDIS_URI')
OsuCommunityCookie = os.environ.get('OSU_COMMUNITY_COOKIE')


@app.route('/', methods=['GET'])
def Home():     # No valid path, return to the doc
    Analytics(request)
    return redirect('https://ninym.top', code=301)


@app.route('/favicon.ico')
def favicon():  # Return favicon
    Analytics(request)
    return send_from_directory('./assets/', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/pixiv/<id>', methods=['GET'])
def PixivParser(id):
    '''Pixiv Pictures Downloader'''
    Analytics(request)
    PixivImgDownload(id)
    return flask.send_from_directory('./cache/', f'{id}_{0}.png', as_attachment=False, download_name=f'{id}.png')


@app.route('/<query>', methods=['GET'])  # First path handler
def parser(query):
    '''Main Function'''
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


@app.route('/<query>/', methods=['GET'])
def SplashAddedHandler(query):
    '''Main Parser'''
    return parser(query)


@app.route('/cache/<file>', methods=['GET'])    # Cache Handler
def cacheHandler(file):
    '''Cache Route for downloading files'''
    Analytics(request)
    return flask.send_from_directory('./cache/', file, as_attachment=False, download_name=file)


@app.route('/gh/<operation>', methods=['GET'])   # Github Handler
def ghHandler(operation):
    '''Github Route'''
    Analytics(request)
    author = request.args.get('author')
    repo = request.args.get('repo')
    ContentType = request.args.get('type')
    if ContentType != 'pic' and ContentType != 'json':
        ContentType = 'pic'
    return ghParser(operation, author, repo, ContentType)


@app.route('/gh/<op>/', methods=['GET'])
def SplashAddedghHandler(op):
    '''Github Route'''
    return ghHandler(op)


@app.route('/url/<token>', methods=['GET', 'POST'])
def UrlHandler(tokan):
    pass

app.register_blueprint(hexo_link_check_blueprint)
# @app.errorhandler(404)  # 404 Handler
# def not_found():
#     Analytics(request)


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


@app.route('/beatmapsets/<int:mapid>', methods=['GET'])
def LongPathParser(mapid):
    novideo = True if request.args.get('novideo') == '1' else False
    return MapDownloader(mapid, OsuCommunityCookie, novideo)


@app.route('/osumap/<int:mapid>', methods=['GET'])
def OsuHandler(mapid):
    novideo = True if request.args.get('novideo') == '1' else False
    return MapDownloader(mapid, OsuCommunityCookie, novideo)


def Analytics(request):
    logger.info('{:=^80}'.format('New request started'))
    logger.info(request.headers)
    logger.info('{:=^80}'.format('New request ended'))
    header = request.headers
    r.get(BaiduAnalytics, headers=header)


if __name__ == '__main__':  # Launcher
    logger.info('New Instance Started.')
    # If debug is set to True, every time when the file is saved the program will reload
    app.run(host='0.0.0.0', port=8080, debug=False)
