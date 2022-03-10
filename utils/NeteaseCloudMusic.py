import requests as r
import bs4
import os
import re


def NeteaseDownload(id):
    song, author = FileInfo(id)
    base = 'https://music.163.com/song/media/outer/url?id='
    file = './song/AppData/' + id + '.mp3'
    filename = id+'.mp3'
    if os.path.exists(file):
        return filename, song, author
    with open(file, 'wb') as f:
        try:
            stream = r.get(base + id, timeout=30)
            print('[NETEASEMUSICDOWNLOAD]Getting song {} - {}, returned status_code {}'.format(author, song, stream.status_code))
            f.write(stream.content)
        except TimeoutError:
            return False, None, None
    return filename, song, author


def FileInfo(id):   # Get the information of the song, including name and author
    TargetWebInfo=r.get('https://music.163.com/song?id=' + id)
    html=TargetWebInfo.content
    bf=bs4.BeautifulSoup(html, "lxml")
    song=str(list(bf.find_all('em', class_="f-ff2"))[0])
    author=str(list(bf.find_all('a', class_='s-fc7'))[1])
    song=song.replace('<em class="f-ff2">', '').replace('</em>', '')
    ReplaceLink=re.findall(r'<a class="s-fc7" href=".+">', author)
    for i in ReplaceLink:
        author=author.replace(i, '')
    author=author.replace('</a>', '')
    ForbiddenCharacters=[('\\', ' '), ('/', ' '), (':', '：'),
                           ('*', ' '), ('?', '？'), ('<', ' '), ('>', ' '), ('|', '丨')]
    for i in ForbiddenCharacters:
        song=song.replace(i[0], i[1])
    return song, author
