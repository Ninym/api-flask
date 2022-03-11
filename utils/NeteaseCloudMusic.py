import requests as r
import bs4
import os
import re


def NeteaseDownload(id, ContentType):
    if ContentType == 'attachment':
        song, author = FileInfo(id)
        # If the song id doesn't map to a song, this will return.
        if song == None and author == None:
            return False, 'Not Found', 'Not Found'
        base = 'https://music.163.com/song/media/outer/url?id='
        file = './cache/' + id + '.mp3'
        filename = id+'.mp3'
        if os.path.exists(file):
            return filename, song, author
        try:
            stream = r.get(base + id, timeout=30)
        except TimeoutError:
            return False, None, None
        if 'u-errlg u-errlg-404' in stream.text:    # Some VIP songs cannot be downloaded
            print(
                '[NETEASEMUSICDOWNLOAD] Failed while getting the resources and information of a song.')
            return False, 404, 404
        print('[NETEASEMUSICDOWNLOAD] Getting song {} - {}, returned status_code {}'.format(
            author, song, stream.status_code))
        with open(file, 'wb') as f:
            f.write(stream.content)
        return filename, song, author
    else:
        base = 'https://music.163.com/song/media/outer/url?id='
        song, author = FileInfo(id)
        if song == None and author == None:
            return {'code': -2, 'msg': 'It seems that id {} is not a valid song id.'.format(id)}
        try:
            stream = r.get(base + id, timeout=30)
        except TimeoutError:
            return {'code': -3, 'msg': 'Timed out. Please try again later.'}
        if stream.url == "https://music.163.com/404":
            return {'code': 200, 'link': None, 'name': song, 'author': author, 'msg': 'Cannot fetch download link.'}
        return {'code': 200, 'link': stream.url, 'name': song, 'author': author, 'msg': 'Success'}


def FileInfo(id):   # Get the information of the song, including name and author
    TargetWebInfo = r.get('https://music.163.com/song?id=' + id)
    html = TargetWebInfo.content
    bf = bs4.BeautifulSoup(html, "lxml")
    try:
        song = str(list(bf.find_all('em', class_="f-ff2"))[0])
        song = song.replace('<em class="f-ff2">', '').replace('</em>', '')
        ForbiddenCharacters = [('\\', ' '), ('/', ' '), (':', '：'),
                               ('*', ' '), ('?', '？'), ('<', ' '), ('>', ' '), ('|', '丨')]
        for i in ForbiddenCharacters:
            song = song.replace(i[0], i[1])
    except:
        song = None
    try:
        author = str(list(bf.find_all('a', class_='s-fc7'))[1])
        ReplaceLink = re.findall(r'<a class="s-fc7" href=".+">', author)
        for i in ReplaceLink:
            author = author.replace(i, '')
        author = author.replace('</a>', '')
        if author == '${escape(x.beRepliedUser.nickname)}':
            author = None
    except:
        author = None
    return song, author
